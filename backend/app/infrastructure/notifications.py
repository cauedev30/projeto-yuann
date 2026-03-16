from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from app.db.models.event import ContractEvent, Notification


class EmailSender(Protocol):
    def send_email(self, *, recipient: str, subject: str, body: str) -> bool: ...


class NoopEmailSender:
    def send_email(self, *, recipient: str, subject: str, body: str) -> bool:
        return True


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
