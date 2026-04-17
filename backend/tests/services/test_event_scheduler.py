from app.services.event_scheduler import build_contract_events


def test_event_scheduler_creates_renewal_and_expiration_events() -> None:
    metadata = {
        "signature_date": "2026-03-01",
        "start_date": "2026-04-01",
        "term_months": 60,
        "end_date": "2031-03-31",
        "critical_events": [],
    }

    events = build_contract_events(
        metadata, default_lead_times={"renewal": 180, "expiration": 30}
    )

    event_types = [event.event_type for event in events]
    assert "renewal" in event_types
    assert "expiration" in event_types


def test_event_scheduler_generates_full_schedule_with_derivation_metadata() -> None:
    metadata = {
        "signature_date": "2026-03-01",
        "start_date": "2026-04-01",
        "term_months": 60,
        "end_date": "2031-03-31",
        "financial_terms": {
            "grace_period_months": 3,
            "readjustment_type": "annual",
        },
        "critical_events": [],
    }

    events = build_contract_events(metadata)
    serialized = [
        {
            "event_type": event.event_type,
            "event_date": event.event_date.isoformat(),
            "lead_time_days": event.lead_time_days,
            "metadata": event.metadata,
        }
        for event in events
    ]

    assert serialized[0] == {
        "event_type": "renewal",
        "event_date": "2030-10-02",
        "lead_time_days": 180,
        "metadata": {"derived_from": ["end_date"]},
    }
    assert serialized[1] == {
        "event_type": "expiration",
        "event_date": "2031-03-31",
        "lead_time_days": 30,
        "metadata": {"derived_from": ["end_date"]},
    }

    notification_events = [
        e for e in serialized if e.get("metadata", {}).get("notification_sequence")
    ]
    assert len(notification_events) == 3
    sequences = [e["metadata"]["notification_sequence"] for e in notification_events]
    assert sequences == ["12_months_before", "9_months_before", "7_months_before"]

    readjustment = [e for e in serialized if e["event_type"] == "readjustment"]
    assert len(readjustment) == 1
    assert readjustment[0] == {
        "event_type": "readjustment",
        "event_date": "2027-04-01",
        "lead_time_days": 30,
        "metadata": {
            "derived_from": ["start_date", "financial_terms.readjustment_type"]
        },
    }

    grace = [e for e in serialized if e["event_type"] == "grace_period_end"]
    assert len(grace) == 1
    assert grace[0] == {
        "event_type": "grace_period_end",
        "event_date": "2026-07-01",
        "lead_time_days": 15,
        "metadata": {
            "derived_from": ["start_date", "financial_terms.grace_period_months"]
        },
    }
