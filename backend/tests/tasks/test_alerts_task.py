from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.db.models.contract import Contract
from app.db.models.event import ContractEvent, EventType, Notification
from app.domain.notifications import dismiss_notification
from app.tasks.alerts import process_due_events


def make_contract_event(session, *, days_until_due: int, event_type: str) -> ContractEvent:
    today = date(2026, 4, 1)
    contract = Contract(
        title="Loja Centro",
        external_reference=f"LOC-{event_type}",
        status="active",
    )
    event = ContractEvent(
        event_type=EventType(event_type),
        event_date=today + timedelta(days=days_until_due),
        lead_time_days=30,
        metadata_json={"notification_recipient": "alerts@example.com"},
    )
    contract.events.append(event)
    session.add(contract)
    session.commit()
    session.refresh(event)
    return event


def test_alert_worker_creates_email_notification_for_due_event(session) -> None:
    due_event = make_contract_event(session=session, days_until_due=30, event_type="expiration")

    result = process_due_events(session=session, today="2026-04-01")

    notifications = session.query(Notification).filter_by(contract_event_id=due_event.id).all()

    assert result.sent == 1
    assert result.skipped == 0
    assert len(notifications) == 1
    assert notifications[0].status == "success"


def test_process_due_events_skips_already_sent(session) -> None:
    due_event = make_contract_event(session=session, days_until_due=30, event_type="expiration")

    first_result = process_due_events(session=session, today="2026-04-01")
    second_result = process_due_events(session=session, today="2026-04-01")

    notifications = session.query(Notification).filter_by(contract_event_id=due_event.id).all()

    assert first_result.sent == 1
    assert second_result.sent == 0
    assert second_result.skipped == 1
    assert len(notifications) == 1


def test_process_due_events_creates_new_for_next_day(session) -> None:
    due_event = make_contract_event(session=session, days_until_due=30, event_type="expiration")

    first_result = process_due_events(session=session, today="2026-04-01")
    second_result = process_due_events(session=session, today="2026-04-02")

    notifications = session.query(Notification).filter_by(contract_event_id=due_event.id).order_by(Notification.created_at.asc()).all()

    assert first_result.sent == 1
    assert second_result.sent == 1
    assert len(notifications) == 2
    assert notifications[0].idempotency_key != notifications[1].idempotency_key


def test_dismissed_notification_does_not_block_new_alerts(session) -> None:
    due_event = make_contract_event(session=session, days_until_due=30, event_type="expiration")

    first_result = process_due_events(session=session, today="2026-04-01")
    first_notification = session.query(Notification).filter_by(contract_event_id=due_event.id).one()
    dismiss_notification(first_notification, now=datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc))
    session.commit()

    second_result = process_due_events(session=session, today="2026-04-02")
    notifications = session.query(Notification).filter_by(contract_event_id=due_event.id).order_by(Notification.created_at.asc()).all()

    assert first_result.sent == 1
    assert second_result.sent == 1
    assert len(notifications) == 2
    assert notifications[0].dismissed_at is not None
    assert notifications[1].dismissed_at is None
