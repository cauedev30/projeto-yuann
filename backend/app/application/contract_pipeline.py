from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.contract_versions import (
    build_version_snapshot,
    persist_version_snapshot,
    replace_contract_events,
)
from app.db.models.contract import Contract, ContractVersion
from app.domain.clause_extraction import extract_clauses
from app.domain.contract_metadata import extract_contract_metadata
from app.domain.events import build_contract_events


def run_contract_pipeline(
    session: Session,
    contract: Contract,
    contract_version: ContractVersion,
) -> None:
    """Full pipeline: extract metadata, generate events, and extract clauses.

    Use for non-signed contracts. For signed contracts, use process_signed_contract_archive
    (which handles metadata+events).
    """
    text = contract_version.text_content
    if not text:
        return

    metadata_result = extract_contract_metadata(text)

    contract.signature_date = metadata_result.signature_date
    contract.start_date = metadata_result.start_date
    contract.end_date = metadata_result.end_date
    contract.term_months = metadata_result.term_months
    if metadata_result.parties:
        contract.parties = {"entities": metadata_result.parties}
    if metadata_result.financial_terms:
        contract.financial_terms = metadata_result.financial_terms
    contract.status = "analisado"

    clauses = extract_clauses(text)
    existing_meta = dict(contract_version.extraction_metadata or {})
    existing_meta["field_confidence"] = metadata_result.field_confidence
    existing_meta["match_labels"] = metadata_result.match_labels
    existing_meta["clauses"] = [
        {"title": c.title, "content": c.content, "order_index": c.order_index}
        for c in clauses
    ]
    contract_version.extraction_metadata = existing_meta

    scheduled_events = (
        build_contract_events(metadata_result)
        if metadata_result.ready_for_event_generation
        else []
    )
    persist_version_snapshot(
        contract_version,
        build_version_snapshot(
            metadata_result,
            scheduled_events=scheduled_events,
            contract_version_id=contract_version.id,
        ),
    )

    if metadata_result.ready_for_event_generation:
        replace_contract_events(
            contract,
            scheduled_events=scheduled_events,
            contract_version_id=contract_version.id,
        )
