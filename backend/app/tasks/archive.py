from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.contract import ContractVersion
from app.db.models.event import ContractEvent, EventType
from app.domain.contract_metadata import extract_contract_metadata
from app.domain.events import build_contract_events


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

    contract.events.clear()
    for scheduled_event in build_contract_events(metadata):
        contract.events.append(
            ContractEvent(
                event_type=EventType(scheduled_event.event_type),
                event_date=scheduled_event.event_date,
                lead_time_days=scheduled_event.lead_time_days,
                metadata_json=scheduled_event.metadata,
            )
        )

    session.add(contract)
    session.flush()
