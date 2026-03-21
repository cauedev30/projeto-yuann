from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import fitz
import pytest

from app.infrastructure.pdf_text import (
    PageText,
    extract_contract_pages,
    extract_contract_text,
)


def _create_pdf(tmp_path: Path, pages: list[str]) -> Path:
    """Create a simple PDF with the given page texts."""
    pdf_path = tmp_path / "contract.pdf"
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


class TestPageText:
    def test_page_text_dataclass(self) -> None:
        pt = PageText(page=1, text="hello")
        assert pt.page == 1
        assert pt.text == "hello"


class TestExtractContractPages:
    def test_returns_list_of_page_text(self, tmp_path: Path) -> None:
        pdf_path = _create_pdf(tmp_path, ["Page one content", "Page two content"])
        result = extract_contract_pages(pdf_path)
        assert isinstance(result, list)
        assert all(isinstance(item, PageText) for item in result)

    def test_correct_page_numbers(self, tmp_path: Path) -> None:
        pdf_path = _create_pdf(tmp_path, ["First", "Second", "Third"])
        result = extract_contract_pages(pdf_path)
        assert len(result) == 3
        assert result[0].page == 1
        assert result[1].page == 2
        assert result[2].page == 3

    def test_correct_text_per_page(self, tmp_path: Path) -> None:
        pdf_path = _create_pdf(tmp_path, ["Alpha text", "Beta text"])
        result = extract_contract_pages(pdf_path)
        assert "Alpha text" in result[0].text
        assert "Beta text" in result[1].text

    def test_single_page(self, tmp_path: Path) -> None:
        pdf_path = _create_pdf(tmp_path, ["Only page"])
        result = extract_contract_pages(pdf_path)
        assert len(result) == 1
        assert result[0].page == 1
        assert "Only page" in result[0].text

    def test_ocr_fallback(self, tmp_path: Path) -> None:
        """When embedded text is short, OCR is used per page."""
        pdf_path = _create_pdf(tmp_path, ["", ""])
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR page 1\nOCR page 2"
        result = extract_contract_pages(pdf_path, ocr_client=mock_ocr)
        # With OCR fallback, we still get page-level results
        assert isinstance(result, list)
        assert len(result) >= 1


class TestExtractContractTextBackwardCompat:
    def test_returns_text_extraction_result(self, tmp_path: Path) -> None:
        pdf_path = _create_pdf(tmp_path, ["Hello world content", "Second page here"])
        result = extract_contract_text(pdf_path)
        assert hasattr(result, "text")
        assert hasattr(result, "used_ocr")
        assert hasattr(result, "metadata")
        assert "Hello world content" in result.text
        assert "Second page here" in result.text

    def test_joined_text_preserves_all_pages(self, tmp_path: Path) -> None:
        pdf_path = _create_pdf(tmp_path, ["AAA content", "BBB content", "CCC content"])
        result = extract_contract_text(pdf_path)
        assert "AAA content" in result.text
        assert "BBB content" in result.text
        assert "CCC content" in result.text
