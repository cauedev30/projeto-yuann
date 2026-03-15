from __future__ import annotations

from datetime import date, timedelta

from app.db.models.contract import Contract
from app.db.models.event import ContractEvent, EventType, Notification
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
