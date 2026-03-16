from app.db.models.contract import ContractSource
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
