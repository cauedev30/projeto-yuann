from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.app_factory import create_app
from app.db.models.contract import Contract
from app.infrastructure.storage import LocalStorageService

RETENTION_WINDOW_DAYS = 30


@dataclass(slots=True)
class RetentionCandidate:
    contract_id: str
    external_reference: str
    title: str
    last_analyzed_at: datetime
    storage_keys: list[str]


@dataclass(slots=True)
class FileCleanupFailure:
    storage_key: str
    error: str


@dataclass(slots=True)
class RetentionJobResult:
    mode: str
    now: datetime
    cutoff_at: datetime
    candidates: list[RetentionCandidate] = field(default_factory=list)
    deleted_contract_ids: list[str] = field(default_factory=list)
    deleted_storage_keys: list[str] = field(default_factory=list)
    file_cleanup_failures: list[FileCleanupFailure] = field(default_factory=list)

    @property
    def eligible_contracts_count(self) -> int:
        return len(self.candidates)

    @property
    def deleted_contracts_count(self) -> int:
        return len(self.deleted_contract_ids)

    @property
    def deleted_files_count(self) -> int:
        return len(self.deleted_storage_keys)

    @property
    def file_cleanup_failures_count(self) -> int:
        return len(self.file_cleanup_failures)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _ordered_storage_keys(candidates: Sequence[RetentionCandidate]) -> list[str]:
    storage_keys: list[str] = []
    for candidate in candidates:
        for storage_key in candidate.storage_keys:
            if storage_key not in storage_keys:
                storage_keys.append(storage_key)
    return storage_keys


def _build_candidate(contract: Contract) -> RetentionCandidate:
    assert contract.last_analyzed_at is not None
    versions = sorted(contract.versions, key=lambda version: version.version_number)
    return RetentionCandidate(
        contract_id=contract.id,
        external_reference=contract.external_reference,
        title=contract.title,
        last_analyzed_at=_as_utc(contract.last_analyzed_at),
        storage_keys=[version.storage_key for version in versions],
    )


def purge_expired_inactive_contracts(
    *,
    session: Session,
    storage_service: LocalStorageService,
    now: datetime,
    dry_run: bool,
) -> RetentionJobResult:
    now_utc = _as_utc(now)
    cutoff_at = now_utc - timedelta(days=RETENTION_WINDOW_DAYS)
    stmt = (
        select(Contract)
        .options(selectinload(Contract.versions))
        .where(
            Contract.is_active.is_(False),
            Contract.last_analyzed_at.is_not(None),
        )
        .order_by(Contract.last_analyzed_at.asc(), Contract.id.asc())
    )
    contracts = list(session.scalars(stmt))
    candidates = [
        candidate
        for contract in contracts
        if (candidate := _build_candidate(contract)).last_analyzed_at <= cutoff_at
    ]
    result = RetentionJobResult(
        mode="dry-run" if dry_run else "apply",
        now=now_utc,
        cutoff_at=cutoff_at,
        candidates=candidates,
    )

    if dry_run or not candidates:
        return result

    contracts_by_id = {contract.id: contract for contract in contracts}
    for candidate in candidates:
        session.delete(contracts_by_id[candidate.contract_id])

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    result.deleted_contract_ids = [candidate.contract_id for candidate in candidates]
    for storage_key in _ordered_storage_keys(candidates):
        try:
            storage_service.delete(storage_key)
            result.deleted_storage_keys.append(storage_key)
        except Exception as exc:  # pragma: no cover - exercised via tests
            result.file_cleanup_failures.append(
                FileCleanupFailure(storage_key=storage_key, error=str(exc))
            )

    return result


def _format_candidate(candidate: RetentionCandidate) -> str:
    return (
        f"- contract_id={candidate.contract_id} "
        f"external_reference={candidate.external_reference} "
        f"title={candidate.title!r} "
        f"last_analyzed_at={candidate.last_analyzed_at.isoformat()} "
        f"storage_keys={candidate.storage_keys}"
    )


def _format_failure(failure: FileCleanupFailure) -> str:
    return f"- storage_key={failure.storage_key} error={failure.error}"


def _emit_report(result: RetentionJobResult) -> None:
    print(f"mode: {result.mode}")
    print(f"now_utc: {result.now.isoformat()}")
    print(f"cutoff_utc: {result.cutoff_at.isoformat()}")
    print(f"eligible_contracts: {result.eligible_contracts_count}")
    print(f"removed_contracts: {result.deleted_contracts_count}")
    print(f"removed_files: {result.deleted_files_count}")
    print(f"file_cleanup_failures: {result.file_cleanup_failures_count}")

    if result.candidates:
        print("candidates:")
        for candidate in result.candidates:
            print(_format_candidate(candidate))

    if result.file_cleanup_failures:
        print("cleanup_failures:")
        for failure in result.file_cleanup_failures:
            print(_format_failure(failure))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Expurga contratos inativos cujo last_analyzed_at venceu ha 30 dias ou mais.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Lista os contratos elegiveis sem alterar banco ou filesystem.",
    )
    args = parser.parse_args(argv)

    app = create_app()
    session_factory = app.state.session_factory
    storage_service = app.state.storage_service
    session = session_factory()
    try:
        result = purge_expired_inactive_contracts(
            session=session,
            storage_service=storage_service,
            now=datetime.now(timezone.utc),
            dry_run=args.dry_run,
        )
    except Exception as exc:
        print(f"retention job failed before commit: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()

    _emit_report(result)
    if result.file_cleanup_failures:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
