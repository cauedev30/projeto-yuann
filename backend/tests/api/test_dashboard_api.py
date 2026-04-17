from __future__ import annotations

from datetime import date

from tests.support.dashboard_seed import seed_dashboard_data


def test_get_dashboard_returns_aggregated_operational_snapshot(client) -> None:
    session = client.app.state.session_factory()
    try:
        seed_dashboard_data(session)
    finally:
        session.close()

    response = client.get(
        "/api/dashboard", params={"today": date(2026, 4, 1).isoformat()}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == {
        "active_contracts": 2,
        "critical_findings": 1,
        "expiring_soon": 2,
    }
    assert len(body["expiring_contracts"]) == 2
    assert body["notifications"] == [
        {
            "id": body["notifications"][0]["id"],
            "contract_event_id": body["notifications"][0]["contract_event_id"],
            "channel": "email",
            "recipient": "finance@example.com",
            "status": "pending",
            "sent_at": None,
            "event_type": "readjustment",
            "contract_title": "Loja Norte",
            "external_reference": "LOC-002",
        },
        {
            "id": body["notifications"][1]["id"],
            "contract_event_id": body["notifications"][1]["contract_event_id"],
            "channel": "email",
            "recipient": "alerts@example.com",
            "status": "failed",
            "sent_at": "2026-04-01T09:00:00Z",
            "event_type": "expiration",
            "contract_title": "Loja Norte",
            "external_reference": "LOC-002",
        },
        {
            "id": body["notifications"][2]["id"],
            "contract_event_id": body["notifications"][2]["contract_event_id"],
            "channel": "email",
            "recipient": "ops@example.com",
            "status": "success",
            "sent_at": "2026-03-27T14:00:00Z",
            "event_type": "renewal",
            "contract_title": "Loja Centro",
            "external_reference": "LOC-001",
        },
    ]


def test_get_dashboard_returns_empty_snapshot_when_runtime_state_is_absent(
    client,
) -> None:
    response = client.get(
        "/api/dashboard", params={"today": date(2026, 4, 1).isoformat()}
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": {
            "active_contracts": 0,
            "critical_findings": 0,
            "expiring_soon": 0,
        },
        "expiring_contracts": [],
        "notifications": [],
    }
