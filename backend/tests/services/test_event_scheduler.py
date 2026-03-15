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
