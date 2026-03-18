from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Protocol

from app.db.models.event import ContractEvent, Notification

logger = logging.getLogger(__name__)


class EmailSender(Protocol):
    def send_email(self, *, recipient: str, subject: str, body: str) -> bool: ...


class NoopEmailSender:
    def send_email(self, *, recipient: str, subject: str, body: str) -> bool:
        return True


class SmtpEmailSender:
    def __init__(self, *, host: str = "localhost", port: int = 1025) -> None:
        self._host = host
        self._port = port

    def send_email(self, *, recipient: str, subject: str, body: str) -> bool:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = "alertas@yuann.legal"
        msg["To"] = recipient

        try:
            with smtplib.SMTP(self._host, self._port) as server:
                server.send_message(msg)
            return True
        except Exception:
            logger.exception("Failed to send email to %s", recipient)
            return False


def _build_enriched_body(notification: Notification, event: ContractEvent) -> str:
    event_type = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
    contract = event.contract
    title = contract.title if contract else "Contrato"

    lines = [
        f"Contrato: {title}",
        f"Tipo de evento: {event_type}",
    ]
    if event.event_date:
        lines.append(f"Data do evento: {event.event_date.strftime('%d/%m/%Y')}")
        days_remaining = (event.event_date - datetime.now(timezone.utc).date()).days
        lines.append(f"Dias restantes: {days_remaining}")

    metadata = event.metadata_json or {}
    if "notification_sequence" in metadata:
        lines.append(f"Sequencia de notificacao: {metadata['notification_sequence']}")

    lines.append("")
    lines.append("Este e um alerta automatico do sistema Yuann LegalTech.")
    return "\n".join(lines)


def dispatch_email_notification(
    notification: Notification,
    *,
    event: ContractEvent,
    email_sender: EmailSender | None = None,
) -> bool:
    sender = email_sender or NoopEmailSender()
    event_type = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
    body = _build_enriched_body(notification, event)
    success = sender.send_email(
        recipient=notification.recipient,
        subject=f"Contrato: evento {event_type}",
        body=body,
    )

    notification.status = "success" if success else "failed"
    if success:
        notification.sent_at = datetime.now(timezone.utc)
    return success
