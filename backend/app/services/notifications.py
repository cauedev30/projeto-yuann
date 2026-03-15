from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Protocol

from app.db.models.event import ContractEvent, Notification, NotificationChannel


class EmailSender(Protocol):
    def send_email(self, *, recipient: str, subject: str, body: str) -> bool: ...


class NoopEmailSender:
    def send_email(self, *, recipient: str, subject: str, body: str) -> bool:
        return True


def build_email_notification(event: ContractEvent, *, today: date) -> Notification:
    recipient = "alerts@example.com"
    if event.metadata_json and isinstance(event.metadata_json.get("notification_recipient"), str):
        recipient = event.metadata_json["notification_recipient"]

    return Notification(
        contract_event_id=event.id,
        channel=NotificationChannel.email,
        recipient=recipient,
        status="pending",
        idempotency_key=f"{event.id}:email:{today.isoformat()}",
    )


def dispatch_email_notification(
    notification: Notification,
    *,
    event: ContractEvent,
    email_sender: EmailSender | None = None,
) -> bool:
    sender = email_sender or NoopEmailSender()
    success = sender.send_email(
        recipient=notification.recipient,
        subject=f"Contrato: evento {event.event_type.value}",
        body="Um evento contratual entrou na janela de alerta.",
    )

    notification.status = "success" if success else "failed"
    if success:
        notification.sent_at = datetime.now(timezone.utc)
    return success
