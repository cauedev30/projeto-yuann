from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.contract import Contract, ContractVersion
from app.db.models.event import ContractEvent, EventType
from app.schemas.metadata import ContractMetadataResult, ScheduledEvent


def next_contract_version_number(session: Session, contract: Contract) -> int:
    session.flush()
    current_max = session.scalar(
        select(func.max(ContractVersion.version_number)).where(
            ContractVersion.contract_id == contract.id
        )
    )
    return int(current_max or 0) + 1


def _snapshot_contract_parties(metadata: ContractMetadataResult) -> dict[str, Any] | None:
    if not metadata.parties:
        return None
    return dict(metadata.parties)


def build_contract_snapshot(metadata: ContractMetadataResult) -> dict[str, Any]:
    return {
        "signature_date": metadata.signature_date.isoformat() if metadata.signature_date else None,
        "start_date": metadata.start_date.isoformat() if metadata.start_date else None,
        "end_date": metadata.end_date.isoformat() if metadata.end_date else None,
        "term_months": metadata.term_months,
        "parties": _snapshot_contract_parties(metadata),
        "financial_terms": metadata.financial_terms or None,
        "field_confidence": metadata.field_confidence,
    }


def serialize_scheduled_events(
    scheduled_events: Iterable[ScheduledEvent],
    *,
    contract_version_id: str,
) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for event in scheduled_events:
        metadata = dict(event.metadata)
        metadata["source_contract_version_id"] = contract_version_id
        serialized.append(
            {
                "event_type": event.event_type,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "lead_time_days": event.lead_time_days,
                "metadata": metadata,
            }
        )
    return serialized


def build_version_snapshot(
    metadata: ContractMetadataResult,
    *,
    scheduled_events: Iterable[ScheduledEvent],
    contract_version_id: str,
) -> dict[str, Any]:
    return {
        "contract": build_contract_snapshot(metadata),
        "events": serialize_scheduled_events(
            scheduled_events,
            contract_version_id=contract_version_id,
        ),
    }


def persist_version_snapshot(
    contract_version: ContractVersion,
    snapshot: dict[str, Any],
) -> None:
    metadata = dict(contract_version.extraction_metadata or {})
    metadata["version_snapshot"] = snapshot
    contract_version.extraction_metadata = metadata


def replace_contract_events(
    contract: Contract,
    *,
    scheduled_events: Iterable[ScheduledEvent],
    contract_version_id: str,
) -> None:
    contract.events.clear()
    for event in scheduled_events:
        metadata = dict(event.metadata)
        metadata["source_contract_version_id"] = contract_version_id
        contract.events.append(
            ContractEvent(
                event_type=EventType(event.event_type),
                event_date=event.event_date,
                lead_time_days=event.lead_time_days,
                metadata_json=metadata,
            )
        )


def get_contract_version_snapshot(contract_version: ContractVersion) -> dict[str, Any] | None:
    metadata = contract_version.extraction_metadata or {}
    snapshot = metadata.get("version_snapshot")
    if isinstance(snapshot, dict):
        return snapshot

    signed_snapshot = metadata.get("signed_contract_snapshot")
    if not isinstance(signed_snapshot, dict):
        return None

    fields = signed_snapshot.get("fields") or {}
    parties = fields.get("parties")
    serialized_parties = (
        parties
        if isinstance(parties, dict)
        else {"entities": parties} if parties else None
    )
    return {
        "contract": {
            "signature_date": fields.get("signature_date"),
            "start_date": fields.get("start_date"),
            "end_date": fields.get("end_date"),
            "term_months": fields.get("term_months"),
            "parties": serialized_parties,
            "financial_terms": fields.get("financial_terms") or None,
            "field_confidence": signed_snapshot.get("field_confidence")
            or metadata.get("field_confidence")
            or {},
        },
        "events": [],
    }
