from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.contract_versions import (
    build_version_snapshot,
    persist_version_snapshot,
    replace_contract_events,
)
from app.db.models.contract import ContractVersion
from app.domain.contract_metadata import extract_contract_metadata
from app.domain.events import build_contract_events


def _build_signed_contract_snapshot(metadata) -> dict[str, object]:
    return {
        "fields": {
            "signature_date": metadata.signature_date.isoformat() if metadata.signature_date else None,
            "start_date": metadata.start_date.isoformat() if metadata.start_date else None,
            "end_date": metadata.end_date.isoformat() if metadata.end_date else None,
            "term_months": metadata.term_months,
            "parties": metadata.parties,
            "financial_terms": metadata.financial_terms,
        },
        "field_confidence": metadata.field_confidence,
        "match_labels": metadata.match_labels,
        "ready_for_event_generation": metadata.ready_for_event_generation,
    }


def process_signed_contract_archive(
    session: Session,
    *,
    contract_version: ContractVersion,
) -> None:
    contract = contract_version.contract
    if contract is None:
        return

    metadata = extract_contract_metadata(contract_version.text_content or "")
    contract.signature_date = metadata.signature_date
    contract.start_date = metadata.start_date
    contract.end_date = metadata.end_date
    contract.term_months = metadata.term_months
    contract.parties = {"entities": metadata.parties}
    contract.financial_terms = metadata.financial_terms
    extraction_metadata = dict(contract_version.extraction_metadata or {})
    extraction_metadata["signed_contract_snapshot"] = _build_signed_contract_snapshot(metadata)
    extraction_metadata["field_confidence"] = metadata.field_confidence
    contract_version.extraction_metadata = extraction_metadata
    scheduled_events = build_contract_events(metadata)
    persist_version_snapshot(
        contract_version,
        build_version_snapshot(
            metadata,
            scheduled_events=scheduled_events,
            contract_version_id=contract_version.id,
        ),
    )
    session.add(contract_version)

    replace_contract_events(
        contract,
        scheduled_events=scheduled_events,
        contract_version_id=contract_version.id,
    )

    session.add(contract)
    session.flush()
