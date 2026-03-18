import pytest

from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.db.models.event import ContractEvent
from app.services.storage import LocalStorageService
from tests.support.pdf_factory import build_pdf_with_text

from app.application.contract_upload import upload_contract_file


def test_upload_contract_file_persists_version_and_extraction(
    session,
    workspace_tmp_path,
) -> None:
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")

    result = upload_contract_file(
        session=session,
        title="Loja Centro",
        external_reference="LOC-001",
        source=ContractSource.third_party_draft,
        filename="contract.pdf",
        content=build_pdf_with_text("Prazo de vigencia 60 meses"),
        storage_service=storage_service,
    )

    assert result.contract.title == "Loja Centro"
    assert result.contract_version.source == ContractSource.third_party_draft
    assert result.extraction.text == "Prazo de vigencia 60 meses"


def test_upload_contract_file_rolls_back_state_when_pdf_is_invalid(
    session,
    workspace_tmp_path,
) -> None:
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")

    with pytest.raises(Exception, match="Uploaded file is not a readable PDF"):
        upload_contract_file(
            session=session,
            title="Loja Centro",
            external_reference="LOC-001",
            source=ContractSource.third_party_draft,
            filename="broken.pdf",
            content=b"not-a-real-pdf",
            storage_service=storage_service,
        )

    assert session.query(Contract).all() == []
    assert session.query(ContractVersion).all() == []
    assert list(storage_service.root.iterdir()) == []


def test_upload_signed_contract_persists_snapshot_and_rebuilds_events(
    session,
    workspace_tmp_path,
) -> None:
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")

    result = upload_contract_file(
        session=session,
        title="Loja Centro",
        external_reference="LOC-001",
        source=ContractSource.signed_contract,
        filename="signed-contract.pdf",
        content=build_pdf_with_text(
            "Data de assinatura: 01/03/2026\n"
            "Inicio de vigencia: 01/04/2026\n"
            "Prazo de vigencia: 60 meses\n"
            "Locataria: Franquia XPTO LTDA\n"
            "Carencia de 3 meses\n"
            "Reajuste anual"
        ),
        storage_service=storage_service,
    )

    session.expire_all()
    contract = session.query(Contract).filter_by(external_reference="LOC-001").one()
    version = session.query(ContractVersion).filter_by(contract_id=contract.id).one()
    events = session.query(ContractEvent).filter_by(contract_id=contract.id).all()

    assert contract.signature_date.isoformat() == "2026-03-01"
    assert contract.start_date.isoformat() == "2026-04-01"
    assert contract.end_date.isoformat() == "2031-03-31"
    assert contract.term_months == 60
    assert contract.parties == {"entities": ["Franquia XPTO LTDA"]}
    assert contract.financial_terms == {
        "grace_period_months": 3,
        "readjustment_type": "annual",
    }
    assert version.extraction_metadata == {
        "embedded_text_length": len(result.extraction.text),
        "ocr_attempted": False,
        "signed_contract_snapshot": {
            "fields": {
                "signature_date": "2026-03-01",
                "start_date": "2026-04-01",
                "end_date": "2031-03-31",
                "term_months": 60,
                "parties": ["Franquia XPTO LTDA"],
                "financial_terms": {
                    "grace_period_months": 3,
                    "readjustment_type": "annual",
                },
            },
            "field_confidence": {
                "signature_date": 1.0,
                "start_date": 1.0,
                "term_months": 1.0,
                "end_date": 1.0,
                "parties": 1.0,
                "grace_period_months": 1.0,
                "readjustment_type": 1.0,
                "monthly_rent": 0.0,
                "penalty_months": 0.0,
            },
            "match_labels": {
                "signature_date": "data de assinatura",
                "start_date": "inicio de vigencia",
                "end_date": "prazo de vigencia",
                "term_months": "prazo de vigencia",
                "parties": "locataria",
                "grace_period_months": "carencia de",
                "readjustment_type": "reajuste anual",
            },
            "ready_for_event_generation": True,
        },
        "field_confidence": {
            "signature_date": 1.0,
            "start_date": 1.0,
            "term_months": 1.0,
            "end_date": 1.0,
            "parties": 1.0,
            "grace_period_months": 1.0,
            "readjustment_type": 1.0,
            "monthly_rent": 0.0,
            "penalty_months": 0.0,
        },
    }
    event_types_sorted = sorted(event.event_type.value for event in events)
    assert event_types_sorted.count("renewal") == 1
    assert event_types_sorted.count("readjustment") == 1
    assert event_types_sorted.count("grace_period_end") == 1
    assert event_types_sorted.count("expiration") == 5  # 1 base + 4 notifications

    base_events = {
        event.event_type.value: event.metadata_json
        for event in events
        if not (event.metadata_json or {}).get("notification_sequence")
    }
    assert base_events == {
        "renewal": {
            "derived_from": ["end_date"],
            "source_contract_version_id": version.id,
        },
        "expiration": {
            "derived_from": ["end_date"],
            "source_contract_version_id": version.id,
        },
        "readjustment": {
            "derived_from": ["start_date", "financial_terms.readjustment_type"],
            "source_contract_version_id": version.id,
        },
        "grace_period_end": {
            "derived_from": ["start_date", "financial_terms.grace_period_months"],
            "source_contract_version_id": version.id,
        },
    }

    notification_events = [
        event for event in events
        if (event.metadata_json or {}).get("notification_sequence")
    ]
    assert len(notification_events) == 4


def test_upload_signed_contract_replaces_existing_schedule_with_latest_version(
    session,
    workspace_tmp_path,
) -> None:
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")

    first_result = upload_contract_file(
        session=session,
        title="Loja Centro",
        external_reference="LOC-001",
        source=ContractSource.signed_contract,
        filename="signed-contract-v1.pdf",
        content=build_pdf_with_text(
            "Data de assinatura: 01/03/2026\n"
            "Inicio de vigencia: 01/04/2026\n"
            "Prazo de vigencia: 60 meses"
        ),
        storage_service=storage_service,
    )
    second_result = upload_contract_file(
        session=session,
        title="Loja Centro",
        external_reference="LOC-001",
        source=ContractSource.signed_contract,
        filename="signed-contract-v2.pdf",
        content=build_pdf_with_text(
            "Data de assinatura: 01/03/2027\n"
            "Inicio de vigencia: 01/05/2027\n"
            "Prazo de vigencia: 24 meses"
        ),
        storage_service=storage_service,
    )

    session.expire_all()
    contract = session.query(Contract).filter_by(external_reference="LOC-001").one()
    events = session.query(ContractEvent).filter_by(contract_id=contract.id).all()
    versions = (
        session.query(ContractVersion)
        .filter_by(contract_id=contract.id)
        .order_by(ContractVersion.created_at.asc(), ContractVersion.id.asc())
        .all()
    )

    assert {version.id for version in versions} == {
        first_result.contract_version.id,
        second_result.contract_version.id,
    }
    assert contract.signature_date.isoformat() == "2027-03-01"
    assert contract.start_date.isoformat() == "2027-05-01"
    assert contract.end_date.isoformat() == "2029-04-30"
    assert contract.term_months == 24
    base_events = [e for e in events if not (e.metadata_json or {}).get("notification_sequence")]
    notification_events = [e for e in events if (e.metadata_json or {}).get("notification_sequence")]
    assert sorted(e.event_type.value for e in base_events) == ["expiration", "renewal"]
    assert {e.event_type.value: e.event_date.isoformat() for e in base_events} == {
        "renewal": "2028-11-01",
        "expiration": "2029-04-30",
    }
    assert {
        e.event_type.value: e.metadata_json["source_contract_version_id"]
        for e in base_events
    } == {
        "renewal": second_result.contract_version.id,
        "expiration": second_result.contract_version.id,
    }
    assert len(notification_events) == 4
