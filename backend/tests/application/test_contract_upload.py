import pytest

from app.db.models.contract import Contract, ContractSource, ContractVersion
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
