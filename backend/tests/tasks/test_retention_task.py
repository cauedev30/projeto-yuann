from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.db.models.analysis import ContractAnalysis, ContractAnalysisFinding
from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.db.models.event import ContractEvent, EventType, Notification, NotificationChannel
from app.services.storage import LocalStorageService
from app.tasks.retention import purge_expired_inactive_contracts


class FailingDeleteStorageService(LocalStorageService):
    def __init__(self, root: Path, *, failing_key: str) -> None:
        super().__init__(root)
        self.failing_key = failing_key

    def delete(self, storage_key: str) -> None:
        if storage_key == self.failing_key:
            raise OSError("simulated storage cleanup failure")
        super().delete(storage_key)


def create_contract_graph(
    session,
    storage_service: LocalStorageService,
    *,
    external_reference: str,
    is_active: bool,
    last_analyzed_at: datetime | None,
    version_count: int = 1,
) -> tuple[Contract, list[str]]:
    contract = Contract(
        title=f"Contrato {external_reference}",
        external_reference=external_reference,
        status="analisado",
        is_active=is_active,
        last_analyzed_at=last_analyzed_at,
    )
    storage_keys: list[str] = []

    for version_number in range(1, version_count + 1):
        storage_key = storage_service.store_bytes(
            f"{external_reference}-v{version_number}.pdf",
            f"conteudo-{external_reference}-{version_number}".encode(),
        )
        storage_keys.append(storage_key)

        version = ContractVersion(
            version_number=version_number,
            source=ContractSource.signed_contract,
            original_filename=f"{external_reference}-v{version_number}.pdf",
            storage_key=storage_key,
            text_content=f"texto-{external_reference}-{version_number}",
        )
        analysis = ContractAnalysis(
            contract_version=version,
            policy_version=f"v{version_number}",
            status="completed",
            contract_risk_score=42,
            findings=[
                ContractAnalysisFinding(
                    clause_name="Prazo",
                    status="critical",
                    severity="high",
                    current_summary="Prazo fora da politica.",
                    policy_rule="Prazo minimo de 48 meses.",
                    risk_explanation="Risco juridico.",
                    suggested_adjustment_direction="Ajustar prazo.",
                )
            ],
        )
        event = ContractEvent(
            event_type=EventType.renewal,
            lead_time_days=30,
            metadata_json={"source_contract_version_id": f"{external_reference}-v{version_number}"},
            notifications=[
                Notification(
                    channel=NotificationChannel.email,
                    recipient="ops@example.com",
                    status="pending",
                    idempotency_key=f"{external_reference}:{version_number}",
                )
            ],
        )

        contract.versions.append(version)
        contract.analyses.append(analysis)
        contract.events.append(event)

    session.add(contract)
    session.commit()
    session.refresh(contract)
    return contract, storage_keys


def count_rows(session) -> dict[str, int]:
    session.expire_all()
    return {
        "contracts": session.query(Contract).count(),
        "versions": session.query(ContractVersion).count(),
        "analyses": session.query(ContractAnalysis).count(),
        "findings": session.query(ContractAnalysisFinding).count(),
        "events": session.query(ContractEvent).count(),
        "notifications": session.query(Notification).count(),
    }


def test_purge_removes_inactive_contract_older_than_cutoff(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    contract, storage_keys = create_contract_graph(
        session,
        storage_service,
        external_reference="RET-001",
        is_active=False,
        last_analyzed_at=now - timedelta(days=31),
    )

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.mode == "apply"
    assert result.eligible_contracts_count == 1
    assert result.deleted_contracts_count == 1
    assert result.deleted_files_count == 1
    assert result.file_cleanup_failures_count == 0
    assert result.deleted_contract_ids == [contract.id]
    assert session.get(Contract, contract.id) is None
    assert all(not (storage_service.root / storage_key).exists() for storage_key in storage_keys)


def test_purge_removes_inactive_contract_exactly_at_30_day_boundary(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    contract, _ = create_contract_graph(
        session,
        storage_service,
        external_reference="RET-BOUNDARY",
        is_active=False,
        last_analyzed_at=now - timedelta(days=30),
    )

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.deleted_contract_ids == [contract.id]
    assert session.get(Contract, contract.id) is None


def test_purge_preserves_active_contract_even_when_old(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    contract, storage_keys = create_contract_graph(
        session,
        storage_service,
        external_reference="RET-ACTIVE",
        is_active=True,
        last_analyzed_at=now - timedelta(days=365),
    )

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.eligible_contracts_count == 0
    assert result.deleted_contracts_count == 0
    assert session.get(Contract, contract.id) is not None
    assert all((storage_service.root / storage_key).exists() for storage_key in storage_keys)


def test_purge_preserves_inactive_contract_without_last_analyzed_at(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    contract, storage_keys = create_contract_graph(
        session,
        storage_service,
        external_reference="RET-NO-ANALYSIS",
        is_active=False,
        last_analyzed_at=None,
    )

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.eligible_contracts_count == 0
    assert result.deleted_contracts_count == 0
    assert session.get(Contract, contract.id) is not None
    assert all((storage_service.root / storage_key).exists() for storage_key in storage_keys)


def test_purge_preserves_inactive_contract_inside_retention_window(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    contract, storage_keys = create_contract_graph(
        session,
        storage_service,
        external_reference="RET-WINDOW",
        is_active=False,
        last_analyzed_at=now - timedelta(days=29, hours=23),
    )

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.eligible_contracts_count == 0
    assert result.deleted_contracts_count == 0
    assert session.get(Contract, contract.id) is not None
    assert all((storage_service.root / storage_key).exists() for storage_key in storage_keys)


def test_purge_dry_run_does_not_change_database_or_storage(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    contract, storage_keys = create_contract_graph(
        session,
        storage_service,
        external_reference="RET-DRY",
        is_active=False,
        last_analyzed_at=now - timedelta(days=45),
        version_count=2,
    )
    before_counts = count_rows(session)

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=True,
    )

    assert result.mode == "dry-run"
    assert result.eligible_contracts_count == 1
    assert result.deleted_contracts_count == 0
    assert result.deleted_files_count == 0
    assert result.candidates[0].contract_id == contract.id
    assert result.candidates[0].external_reference == "RET-DRY"
    assert result.candidates[0].storage_keys == storage_keys
    assert count_rows(session) == before_counts
    assert session.get(Contract, contract.id) is not None
    assert all((storage_service.root / storage_key).exists() for storage_key in storage_keys)


def test_purge_real_execution_removes_persisted_graph_via_cascade(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    create_contract_graph(
        session,
        storage_service,
        external_reference="RET-CASCADE",
        is_active=False,
        last_analyzed_at=now - timedelta(days=60),
        version_count=2,
    )

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.deleted_contracts_count == 1
    assert count_rows(session) == {
        "contracts": 0,
        "versions": 0,
        "analyses": 0,
        "findings": 0,
        "events": 0,
        "notifications": 0,
    }


def test_purge_real_execution_removes_physical_files_for_versions(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    _, storage_keys = create_contract_graph(
        session,
        storage_service,
        external_reference="RET-FILES",
        is_active=False,
        last_analyzed_at=now - timedelta(days=60),
        version_count=2,
    )

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.deleted_files_count == 2
    assert result.file_cleanup_failures_count == 0
    assert result.deleted_storage_keys == storage_keys
    assert all(not (storage_service.root / storage_key).exists() for storage_key in storage_keys)


def test_purge_reports_physical_cleanup_failures_after_commit(session, workspace_tmp_path) -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    uploads_root = workspace_tmp_path / "uploads"
    setup_storage = LocalStorageService(uploads_root)
    contract, storage_keys = create_contract_graph(
        session,
        setup_storage,
        external_reference="RET-CLEANUP-FAIL",
        is_active=False,
        last_analyzed_at=now - timedelta(days=90),
        version_count=2,
    )
    storage_service = FailingDeleteStorageService(uploads_root, failing_key=storage_keys[0])

    result = purge_expired_inactive_contracts(
        session=session,
        storage_service=storage_service,
        now=now,
        dry_run=False,
    )

    assert result.deleted_contract_ids == [contract.id]
    assert result.deleted_files_count == 1
    assert result.file_cleanup_failures_count == 1
    assert result.file_cleanup_failures[0].storage_key == storage_keys[0]
    assert "simulated storage cleanup failure" in result.file_cleanup_failures[0].error
    assert session.get(Contract, contract.id) is None
    assert (uploads_root / storage_keys[0]).exists()
    assert not (uploads_root / storage_keys[1]).exists()
