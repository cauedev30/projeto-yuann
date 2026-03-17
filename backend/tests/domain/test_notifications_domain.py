from __future__ import annotations

from datetime import datetime, timezone

from app.db.models.event import Notification, NotificationChannel
from app.domain.notifications import dismiss_notification


def make_notification() -> Notification:
    return Notification(
        contract_event_id="event-1",
        channel=NotificationChannel.email,
        recipient="alerts@example.com",
        status="pending",
        idempotency_key="event-1:email:2026-04-01",
    )


def test_dismiss_sets_dismissed_at() -> None:
    notification = make_notification()
    expected = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)

    dismiss_notification(notification, now=expected)

    assert notification.dismissed_at == expected


def test_dismiss_idempotent_preserves_original_timestamp() -> None:
    original = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)
    notification = make_notification()
    notification.dismissed_at = original

    dismiss_notification(notification, now=datetime(2026, 4, 1, 13, 0, tzinfo=timezone.utc))

    assert notification.dismissed_at == original
