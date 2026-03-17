from __future__ import annotations

from datetime import date

from app.application.dashboard import build_dashboard_snapshot
from tests.support.dashboard_seed import seed_dashboard_data


def test_build_dashboard_snapshot_aggregates_kpis_events_and_notifications(session) -> None:
    seed_dashboard_data(session)

    snapshot = build_dashboard_snapshot(session=session, today=date(2026, 4, 1))

    assert snapshot.summary.active_contracts == 2
    assert snapshot.summary.critical_findings == 1
    assert snapshot.summary.expiring_soon == 2
    assert [event.external_reference for event in snapshot.events] == ["LOC-001", "LOC-002"]
    assert snapshot.events[0].days_until_due == -5
    assert snapshot.events[0].is_overdue is True
    assert snapshot.events[1].days_until_due == 30
    assert snapshot.events[1].lead_time_days == 45
    assert [notification.status for notification in snapshot.notifications] == [
        "pending",
        "failed",
        "success",
    ]
    assert snapshot.notifications[0].event_type == "readjustment"
    assert snapshot.notifications[0].contract_title == "Loja Norte"


def test_build_dashboard_snapshot_returns_empty_snapshot_without_runtime_data(session) -> None:
    snapshot = build_dashboard_snapshot(session=session, today=date(2026, 4, 1))

    assert snapshot.summary.active_contracts == 0
    assert snapshot.summary.critical_findings == 0
    assert snapshot.summary.expiring_soon == 0
    assert snapshot.events == []
    assert snapshot.notifications == []
