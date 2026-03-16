from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.event import ContractEvent, Notification
from app.domain.notifications import build_email_notification, is_event_due
from app.infrastructure.notifications import EmailSender, dispatch_email_notification


@dataclass(slots=True)
class AlertProcessingResult:
    sent: int = 0
    skipped: int = 0
    failed: int = 0


def process_due_events(
    *,
    session: Session,
    today: str | date,
    email_sender: EmailSender | None = None,
) -> AlertProcessingResult:
    reference_date = date.fromisoformat(today) if isinstance(today, str) else today
    result = AlertProcessingResult()

    events = session.scalars(select(ContractEvent).where(ContractEvent.event_date.is_not(None))).all()
    for event in events:
        if not is_event_due(event, today=reference_date):
            continue

        notification = build_email_notification(event, today=reference_date)
        existing = session.scalar(
            select(Notification).where(Notification.idempotency_key == notification.idempotency_key)
        )
        if existing is not None:
            result.skipped += 1
            continue

        session.add(notification)
        session.flush()

        if dispatch_email_notification(notification, event=event, email_sender=email_sender):
            result.sent += 1
        else:
            result.failed += 1

    session.commit()
    return result
