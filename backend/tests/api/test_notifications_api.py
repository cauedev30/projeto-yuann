from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from app.db.models.contract import Contract
from app.db.models.event import ContractEvent, EventType, Notification, NotificationChannel


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def create_notification(
    client,
    *,
    status: str = "pending",
    channel: NotificationChannel = NotificationChannel.email,
    created_at: datetime | None = None,
    dismissed_at: datetime | None = None,
    sent_at: datetime | None = None,
) -> dict[str, object]:
    created_at = created_at or datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)
    notification_id = str(uuid4())
    event_id = str(uuid4())

    session = client.app.state.session_factory()
    try:
        contract = Contract(
            id=str(uuid4()),
            title="Loja Centro",
            external_reference=f"LOC-{notification_id[:8]}",
            status="active",
        )
        event = ContractEvent(
            id=event_id,
            event_type=EventType.expiration,
            event_date=date(2026, 5, 1),
            lead_time_days=30,
            metadata_json={"notification_recipient": "alerts@example.com"},
        )
        contract.events.append(event)

        notification = Notification(
            id=notification_id,
            contract_event_id=event_id,
            channel=channel,
            recipient="alerts@example.com",
            status=status,
            idempotency_key=f"{event_id}:{channel.value}:{created_at.date().isoformat()}:{notification_id[:8]}",
            created_at=created_at,
            updated_at=created_at,
            sent_at=sent_at,
            dismissed_at=dismissed_at,
        )

        session.add(contract)
        session.add(notification)
        session.commit()
    finally:
        session.close()

    return {
        "id": notification_id,
        "contract_event_id": event_id,
        "channel": channel.value,
        "created_at": created_at,
        "sent_at": sent_at,
        "dismissed_at": dismissed_at,
        "status": status,
    }


def test_list_notifications_empty(client) -> None:
    response = client.get("/api/notifications")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_list_notifications_returns_items(client) -> None:
    created = datetime(2026, 4, 2, 10, 30, tzinfo=timezone.utc)
    sent_at = datetime(2026, 4, 2, 10, 45, tzinfo=timezone.utc)
    notification = create_notification(
        client,
        status="success",
        created_at=created,
        sent_at=sent_at,
    )

    response = client.get("/api/notifications")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["id"] == notification["id"]
    assert payload["items"][0]["contract_event_id"] == notification["contract_event_id"]
    assert payload["items"][0]["channel"] == "email"
    assert payload["items"][0]["status"] == "success"
    assert _parse_datetime(payload["items"][0]["created_at"]) == created
    assert _parse_datetime(payload["items"][0]["sent_at"]) == sent_at
    assert payload["items"][0]["dismissed_at"] is None


def test_list_notifications_filter_by_status(client) -> None:
    expected = create_notification(client, status="success")
    create_notification(client, status="failed")

    response = client.get("/api/notifications?status=success")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert [item["id"] for item in response.json()["items"]] == [expected["id"]]


def test_list_notifications_filter_by_channel_and_date_range(client) -> None:
    create_notification(
        client,
        channel=NotificationChannel.email,
        created_at=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc),
    )
    expected = create_notification(
        client,
        channel=NotificationChannel.in_app,
        created_at=datetime(2026, 4, 3, 11, 0, tzinfo=timezone.utc),
    )

    response = client.get("/api/notifications?channel=in_app&from_date=2026-04-02&to_date=2026-04-03")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert [item["id"] for item in response.json()["items"]] == [expected["id"]]


def test_list_notifications_filter_dismissed(client) -> None:
    dismissed = create_notification(
        client,
        dismissed_at=datetime(2026, 4, 2, 12, 0, tzinfo=timezone.utc),
    )
    active = create_notification(client)

    dismissed_response = client.get("/api/notifications?dismissed=true")
    active_response = client.get("/api/notifications?dismissed=false")

    assert dismissed_response.status_code == 200
    assert [item["id"] for item in dismissed_response.json()["items"]] == [dismissed["id"]]
    assert active_response.status_code == 200
    assert [item["id"] for item in active_response.json()["items"]] == [active["id"]]


def test_list_notifications_pagination(client) -> None:
    oldest = create_notification(client, created_at=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc))
    middle = create_notification(client, created_at=datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc))
    create_notification(client, created_at=datetime(2026, 4, 3, 9, 0, tzinfo=timezone.utc))

    response = client.get("/api/notifications?limit=1&offset=1")

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert [item["id"] for item in response.json()["items"]] == [middle["id"]]
    assert oldest["id"] not in [item["id"] for item in response.json()["items"]]


def test_dismiss_notification_success(client) -> None:
    notification = create_notification(client)

    response = client.post(f"/api/notifications/{notification['id']}/dismiss")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == notification["id"]
    assert _parse_datetime(payload["dismissed_at"]) is not None

    session = client.app.state.session_factory()
    try:
        stored = session.get(Notification, notification["id"])
        assert stored is not None
        assert stored.dismissed_at is not None
    finally:
        session.close()


def test_dismiss_notification_idempotent(client) -> None:
    notification = create_notification(client)

    first_response = client.post(f"/api/notifications/{notification['id']}/dismiss")
    second_response = client.post(f"/api/notifications/{notification['id']}/dismiss")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["dismissed_at"] == first_response.json()["dismissed_at"]


def test_dismiss_notification_not_found(client) -> None:
    response = client.post(f"/api/notifications/{uuid4()}/dismiss")

    assert response.status_code == 404
    assert response.json() == {"detail": "Notification not found"}


def test_dismiss_bulk(client) -> None:
    first = create_notification(client)
    second = create_notification(client)
    already_dismissed = create_notification(
        client,
        dismissed_at=datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc),
    )

    response = client.post(
        "/api/notifications/dismiss-bulk",
        json={"ids": [first["id"], first["id"], second["id"], already_dismissed["id"]]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dismissed_count"] == 2
    assert {item["id"] for item in payload["items"]} == {
        first["id"],
        second["id"],
        already_dismissed["id"],
    }
