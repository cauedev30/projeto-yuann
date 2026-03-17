from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models.event import NotificationChannel


class NotificationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_event_id: str
    channel: NotificationChannel
    recipient: str
    status: str
    idempotency_key: str
    created_at: datetime
    sent_at: datetime | None = None
    dismissed_at: datetime | None = None

    @field_validator("created_at", "sent_at", "dismissed_at", mode="before")
    @classmethod
    def normalize_utc(cls, value: datetime | None) -> datetime | None:
        if value is None or value.tzinfo is not None:
            return value
        return value.replace(tzinfo=timezone.utc)


class NotificationListResponse(BaseModel):
    items: list[NotificationListItem] = Field(default_factory=list)
    total: int = 0


class NotificationDismissBulkRequest(BaseModel):
    ids: list[str] = Field(min_length=1)


class NotificationDismissBulkResponse(BaseModel):
    dismissed_count: int
    items: list[NotificationListItem] = Field(default_factory=list)
