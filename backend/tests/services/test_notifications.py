from datetime import date

from app.db.models.event import ContractEvent, EventType, NotificationChannel
from app.services.notifications import build_email_notification


def test_build_email_notification_creates_deterministic_idempotency_key() -> None:
    event = ContractEvent(
        id="event-1",
        event_type=EventType.expiration,
        lead_time_days=30,
        metadata_json={"notification_recipient": "alerts@example.com"},
    )

    notification = build_email_notification(event=event, today=date(2026, 4, 1))

    assert notification.channel == NotificationChannel.email
    assert notification.idempotency_key == "event-1:email:2026-04-01"
