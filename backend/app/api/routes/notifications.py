from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.application.alerts import process_due_events
from app.db.models.event import Notification, NotificationChannel
from app.domain.notifications import dismiss_notification
from app.schemas.notification import (
    NotificationDismissBulkRequest,
    NotificationDismissBulkResponse,
    NotificationListItem,
    NotificationListResponse,
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

NotificationStatus = Literal["pending", "success", "failed"]


def _serialize_notification(notification: Notification) -> NotificationListItem:
    return NotificationListItem.model_validate(notification)


def _notification_conditions(
    *,
    status: NotificationStatus | None,
    channel: NotificationChannel | None,
    dismissed: bool | None,
    from_date: date | None,
    to_date: date | None,
) -> list[object]:
    conditions: list[object] = []

    if status is not None:
        conditions.append(Notification.status == status)
    if channel is not None:
        conditions.append(Notification.channel == channel)
    if dismissed is True:
        conditions.append(Notification.dismissed_at.is_not(None))
    elif dismissed is False:
        conditions.append(Notification.dismissed_at.is_(None))
    if from_date is not None:
        conditions.append(
            Notification.created_at
            >= datetime.combine(from_date, time.min, tzinfo=timezone.utc)
        )
    if to_date is not None:
        conditions.append(
            Notification.created_at
            < datetime.combine(
                to_date + timedelta(days=1), time.min, tzinfo=timezone.utc
            )
        )

    return conditions


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    status: NotificationStatus | None = None,
    channel: NotificationChannel | None = None,
    dismissed: bool | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> NotificationListResponse:
    conditions = _notification_conditions(
        status=status,
        channel=channel,
        dismissed=dismissed,
        from_date=from_date,
        to_date=to_date,
    )
    total = (
        session.scalar(
            select(func.count()).select_from(Notification).where(*conditions)
        )
        or 0
    )
    notifications = session.scalars(
        select(Notification)
        .where(*conditions)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    items = [_serialize_notification(notification) for notification in notifications]
    return NotificationListResponse(items=items, total=total)


@router.post("/{notification_id}/dismiss", response_model=NotificationListItem)
@router.patch(
    "/{notification_id}/dismiss",
    response_model=NotificationListItem,
    include_in_schema=False,
)
def dismiss_notification_endpoint(
    notification_id: str,
    session: Session = Depends(get_session),
) -> NotificationListItem:
    notification = session.get(Notification, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    dismiss_notification(notification, now=datetime.now(timezone.utc))
    session.commit()
    session.refresh(notification)
    return _serialize_notification(notification)


@router.post("/dismiss-bulk", response_model=NotificationDismissBulkResponse)
def dismiss_notifications_bulk(
    payload: NotificationDismissBulkRequest,
    session: Session = Depends(get_session),
) -> NotificationDismissBulkResponse:
    ordered_ids = list(dict.fromkeys(payload.ids))
    notifications = session.scalars(
        select(Notification).where(Notification.id.in_(ordered_ids))
    ).all()
    notifications_by_id = {
        notification.id: notification for notification in notifications
    }
    ordered_notifications = [
        notifications_by_id[notification_id]
        for notification_id in ordered_ids
        if notification_id in notifications_by_id
    ]

    now = datetime.now(timezone.utc)
    dismissed_count = 0
    for notification in ordered_notifications:
        before = notification.dismissed_at
        dismiss_notification(notification, now=now)
        if before is None and notification.dismissed_at is not None:
            dismissed_count += 1

    session.commit()
    for notification in ordered_notifications:
        session.refresh(notification)

    return NotificationDismissBulkResponse(
        dismissed_count=dismissed_count,
        items=[
            _serialize_notification(notification)
            for notification in ordered_notifications
        ],
    )


@router.post("/process-due", status_code=200)
def process_due_notifications(
    request: Request,
    session: Session = Depends(get_session),
) -> dict:
    """Trigger processing of due events and create notifications.

    Intended to be called by a cron job or scheduler on a daily basis.
    """
    email_sender = getattr(request.app.state, "email_sender", None)
    result = process_due_events(
        session=session,
        today=date.today(),
        email_sender=email_sender,
    )
    return {"sent": result.sent, "skipped": result.skipped, "failed": result.failed}
