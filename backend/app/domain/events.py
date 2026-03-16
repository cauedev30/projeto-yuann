from __future__ import annotations

import calendar
from datetime import date

from app.schemas.metadata import ContractMetadataResult, ScheduledEvent


def _add_months(base_date: date, months: int) -> date:
    zero_based_month = base_date.month - 1 + months
    year = base_date.year + zero_based_month // 12
    month = zero_based_month % 12 + 1
    day = min(base_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def build_contract_events(
    metadata: ContractMetadataResult | dict[str, object],
    *,
    default_lead_times: dict[str, int] | None = None,
) -> list[ScheduledEvent]:
    defaults = {"renewal": 180, "expiration": 30, "readjustment": 30, "grace_period_end": 15}
    if default_lead_times:
        defaults.update(default_lead_times)

    if isinstance(metadata, dict):
        metadata = ContractMetadataResult.model_validate(metadata)

    events: list[ScheduledEvent] = []
    if metadata.end_date is not None:
        events.append(
            ScheduledEvent(
                event_type="renewal",
                event_date=metadata.end_date,
                lead_time_days=defaults["renewal"],
                metadata={"derived_from": ["end_date"]},
            )
        )
        events.append(
            ScheduledEvent(
                event_type="expiration",
                event_date=metadata.end_date,
                lead_time_days=defaults["expiration"],
                metadata={"derived_from": ["end_date"]},
            )
        )

    if metadata.start_date is not None and metadata.financial_terms.get("readjustment_type") == "annual":
        events.append(
            ScheduledEvent(
                event_type="readjustment",
                event_date=_add_months(metadata.start_date, 12),
                lead_time_days=defaults["readjustment"],
                metadata={"derived_from": ["start_date", "financial_terms.readjustment_type"]},
            )
        )

    grace_months = metadata.financial_terms.get("grace_period_months")
    if metadata.start_date is not None and isinstance(grace_months, int):
        events.append(
            ScheduledEvent(
                event_type="grace_period_end",
                event_date=_add_months(metadata.start_date, grace_months),
                lead_time_days=defaults["grace_period_end"],
                metadata={"derived_from": ["start_date", "financial_terms.grace_period_months"]},
            )
        )

    return events
