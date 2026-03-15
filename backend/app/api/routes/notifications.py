from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.db.models.event import Notification

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_event_id: str
    channel: str
    recipient: str
    status: str
    idempotency_key: str
    sent_at: datetime | None = None


class NotificationListResponse(BaseModel):
    items: list[NotificationListItem]


@router.get("", response_model=NotificationListResponse)
def list_notifications(session: Session = Depends(get_session)) -> NotificationListResponse:
    notifications = session.scalars(select(Notification).order_by(Notification.created_at.desc())).all()
    items = [
        NotificationListItem(
            id=notification.id,
            contract_event_id=notification.contract_event_id,
            channel=notification.channel.value,
            recipient=notification.recipient,
            status=notification.status,
            idempotency_key=notification.idempotency_key,
            sent_at=notification.sent_at,
        )
        for notification in notifications
    ]
    return NotificationListResponse(items=items)
