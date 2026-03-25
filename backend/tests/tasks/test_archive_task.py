from __future__ import annotations

from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.tasks.archive import process_signed_contract_archive


def make_contract_version(session, *, text_content: str = "") -> ContractVersion:
    contract = Contract(
        title="Contrato Teste",
        external_reference="ARCH-001",
        status="active",
    )
    version = ContractVersion(
        version_number=1,
        source=ContractSource.signed_contract,
        original_filename="contrato.pdf",
        storage_key="uploads/contrato.pdf",
        text_content=text_content,
    )
    contract.versions.append(version)
    session.add(contract)
    session.commit()
    session.refresh(version)
    return version


def test_process_signed_contract_archive_persists_field_confidence(session) -> None:
    text = (
        "assinatura: 01/01/2025\n"
        "inicio de vigencia: 01/02/2025\n"
        "prazo de vigencia: 12 meses\n"
        "locataria: Empresa XYZ Ltda."
    )
    version = make_contract_version(session=session, text_content=text)

    process_signed_contract_archive(session=session, contract_version=version)
    session.refresh(version)

    assert version.extraction_metadata is not None
    assert "field_confidence" in version.extraction_metadata
    confidence = version.extraction_metadata["field_confidence"]
    assert confidence["signature_date"] == 1.0
    assert confidence["start_date"] == 1.0
    assert confidence["term_months"] == 1.0
    assert confidence["parties"] == 1.0


def test_process_signed_contract_archive_merges_existing_extraction_metadata(session) -> None:
    version = make_contract_version(session=session, text_content="")
    version.extraction_metadata = {"ocr_confidence": 0.95}
    session.commit()

    process_signed_contract_archive(session=session, contract_version=version)
    session.refresh(version)

    assert version.extraction_metadata is not None
    assert "ocr_confidence" in version.extraction_metadata
    assert "field_confidence" in version.extraction_metadata
    assert version.extraction_metadata["ocr_confidence"] == 0.95


def test_process_signed_contract_archive_returns_early_when_no_contract(session) -> None:
    version = ContractVersion(
        version_number=1,
        source=ContractSource.signed_contract,
        original_filename="contrato.pdf",
        storage_key="uploads/contrato.pdf",
        text_content="",
    )
    # version.contract is None — should return without error
    process_signed_contract_archive(session=session, contract_version=version)

    assert version.extraction_metadata is None
