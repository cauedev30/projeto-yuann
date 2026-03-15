from pathlib import Path

from tests.support.pdf_factory import build_image_only_pdf, build_pdf_with_text

from app.services.pdf_text import extract_contract_text


class FakeOcrClient:
    def __init__(self, text: str) -> None:
        self.text = text

    def extract_text(self, pdf_path: Path) -> str:
        return self.text


def test_extract_text_prefers_embedded_text(workspace_tmp_path) -> None:
    pdf_path = workspace_tmp_path / "contract.pdf"
    pdf_path.write_bytes(build_pdf_with_text("Prazo de vigencia 60 meses"))

    result = extract_contract_text(pdf_path)

    assert result.text == "Prazo de vigencia 60 meses"
    assert result.used_ocr is False


def test_extract_text_falls_back_to_ocr_when_pdf_has_no_text(workspace_tmp_path) -> None:
    pdf_path = workspace_tmp_path / "scan.pdf"
    pdf_path.write_bytes(build_image_only_pdf())

    result = extract_contract_text(pdf_path, ocr_client=FakeOcrClient("Contrato assinado"))

    assert result.text == "Contrato assinado"
    assert result.used_ocr is True
