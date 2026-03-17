from __future__ import annotations

from datetime import date, datetime, timezone

from pydantic import BaseModel, field_serializer


class DashboardSummaryResponse(BaseModel):
    active_contracts: int
    critical_findings: int
    expiring_soon: int


class DashboardEventResponse(BaseModel):
    id: str
    event_type: str
    event_date: date
    lead_time_days: int
    contract_id: str
    contract_title: str
    external_reference: str
    days_until_due: int
    is_overdue: bool


class DashboardNotificationResponse(BaseModel):
    id: str
    contract_event_id: str
    channel: str
    recipient: str
    status: str
    sent_at: datetime | None = None
    event_type: str
    contract_title: str
    external_reference: str

    @field_serializer("sent_at")
    def serialize_sent_at(self, sent_at: datetime | None) -> str | None:
        if sent_at is None:
            return None

        normalized = sent_at if sent_at.tzinfo is not None else sent_at.replace(tzinfo=timezone.utc)
        return normalized.isoformat().replace("+00:00", "Z")


class DashboardSnapshotResponse(BaseModel):
    summary: DashboardSummaryResponse
    events: list[DashboardEventResponse]
    notifications: list[DashboardNotificationResponse]
