from __future__ import annotations

from datetime import date, datetime, timedelta

import os

from app.db.models.event import ContractEvent, Notification, NotificationChannel

_DEFAULT_RECIPIENT = os.environ.get(
    "NOTIFICATION_RECIPIENT", "alerts@legalboard.com.br"
)


def _recipient_for_event(event: ContractEvent, user_email: str | None = None) -> str:
    if event.metadata_json and isinstance(
        event.metadata_json.get("notification_recipient"), str
    ):
        return event.metadata_json["notification_recipient"]
    if user_email:
        return user_email
    contract = event.contract
    if contract and contract.parties and isinstance(contract.parties, dict):
        owner_email = contract.parties.get("notification_email")
        if isinstance(owner_email, str) and owner_email:
            return owner_email
    return _DEFAULT_RECIPIENT


def is_event_due(event: ContractEvent, *, today: date) -> bool:
    if event.event_date is None:
        return False
    trigger_date = event.event_date - timedelta(days=event.lead_time_days)
    return trigger_date <= today


def build_email_notification(
    event: ContractEvent, *, today: date, user_email: str | None = None
) -> Notification:
    return Notification(
        contract_event_id=event.id,
        channel=NotificationChannel.email,
        recipient=_recipient_for_event(event, user_email=user_email),
        status="pending",
        idempotency_key=f"{event.id}:email:{today.isoformat()}",
    )


def dismiss_notification(notification: Notification, *, now: datetime) -> None:
    if notification.dismissed_at is None:
        notification.dismissed_at = now
