from app.services.event_scheduler import build_contract_events


def test_event_scheduler_creates_renewal_and_expiration_events() -> None:
    metadata = {
        "signature_date": "2026-03-01",
        "start_date": "2026-04-01",
        "term_months": 60,
        "end_date": "2031-03-31",
        "critical_events": [],
    }

    events = build_contract_events(metadata, default_lead_times={"renewal": 180, "expiration": 30})

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
    serialized = {
        event.event_type: {
            "event_date": event.event_date.isoformat(),
            "lead_time_days": event.lead_time_days,
            "metadata": event.metadata,
        }
        for event in events
    }

    assert serialized == {
        "renewal": {
            "event_date": "2031-03-31",
            "lead_time_days": 180,
            "metadata": {"derived_from": ["end_date"]},
        },
        "expiration": {
            "event_date": "2031-03-31",
            "lead_time_days": 30,
            "metadata": {"derived_from": ["end_date"]},
        },
        "readjustment": {
            "event_date": "2027-04-01",
            "lead_time_days": 30,
            "metadata": {"derived_from": ["start_date", "financial_terms.readjustment_type"]},
        },
        "grace_period_end": {
            "event_date": "2026-07-01",
            "lead_time_days": 15,
            "metadata": {"derived_from": ["start_date", "financial_terms.grace_period_months"]},
        },
    }
