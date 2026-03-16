from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ContractMetadataResult(BaseModel):
    signature_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    term_months: int | None = None
    parties: list[str] = Field(default_factory=list)
    financial_terms: dict[str, object] = Field(default_factory=dict)
    critical_events: list[dict[str, object]] = Field(default_factory=list)
    field_confidence: dict[str, float] = Field(default_factory=dict)
    match_labels: dict[str, str] = Field(default_factory=dict)
    ready_for_event_generation: bool = False


class ScheduledEvent(BaseModel):
    event_type: str
    event_date: date
    lead_time_days: int
    metadata: dict[str, object] = Field(default_factory=dict)
