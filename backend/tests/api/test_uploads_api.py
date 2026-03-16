from app.db.models.contract import Contract, ContractSource, ContractVersion
from tests.support.pdf_factory import build_pdf_with_text


def test_upload_contract_creates_version_and_persists_extracted_text(client) -> None:
    pdf_bytes = build_pdf_with_text("Prazo de vigencia 60 meses")

    response = client.post(
        "/api/uploads/contracts",
        data={
            "title": "Loja Centro",
            "external_reference": "LOC-001",
            "source": "third_party_draft",
        },
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json()["source"] == "third_party_draft"
    assert response.json()["used_ocr"] is False
    assert response.json()["text"] == "Prazo de vigencia 60 meses"

    session = client.app.state.session_factory()
    try:
        contract = session.query(Contract).filter_by(external_reference="LOC-001").one()
        version = session.query(ContractVersion).filter_by(contract_id=contract.id).one()
    finally:
        session.close()

    assert contract.title == "Loja Centro"
    assert version.source == ContractSource.third_party_draft
    assert version.text_content == "Prazo de vigencia 60 meses"


def test_upload_contract_rejects_invalid_pdf_without_persisting_partial_records(client) -> None:
    response = client.post(
        "/api/uploads/contracts",
        data={
            "title": "Loja Centro",
            "external_reference": "LOC-001",
            "source": "third_party_draft",
        },
        files={"file": ("broken.pdf", b"not-a-real-pdf", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Uploaded file is not a readable PDF"}

    session = client.app.state.session_factory()
    try:
        contracts = session.query(Contract).all()
        versions = session.query(ContractVersion).all()
    finally:
        session.close()

    assert contracts == []
    assert versions == []
