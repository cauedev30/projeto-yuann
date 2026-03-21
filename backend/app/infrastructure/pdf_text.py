from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz

from app.infrastructure.ocr import OCRClient


class TextExtractionError(Exception):
    pass


@dataclass(slots=True)
class PageText:
    page: int
    text: str


@dataclass(slots=True)
class TextExtractionResult:
    text: str
    used_ocr: bool
    metadata: dict[str, object]


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def extract_contract_pages(
    pdf_path: Path,
    *,
    ocr_client: OCRClient | None = None,
) -> list[PageText]:
    """Extract text from each page of a PDF, returning per-page results.

    Pages are 1-indexed.  When embedded text is insufficient and an
    *ocr_client* is provided, OCR output is returned as a single
    ``PageText`` entry (page=1) because the OCR client operates on the
    whole document.
    """
    try:
        with fitz.open(pdf_path) as document:
            pages: list[PageText] = [
                PageText(page=page_num + 1, text=_normalize_text(page.get_text("text")))
                for page_num, page in enumerate(document)
            ]
    except fitz.FileDataError as exc:
        raise TextExtractionError("Uploaded file is not a readable PDF") from exc

    embedded_text = " ".join(p.text for p in pages)

    if len(embedded_text) >= 10 or ocr_client is None:
        return pages

    ocr_text = _normalize_text(ocr_client.extract_text(pdf_path))
    return [PageText(page=i + 1, text=part) for i, part in enumerate(ocr_text.split("\n"))] or [
        PageText(page=1, text=ocr_text)
    ]


def extract_contract_text(
    pdf_path: Path,
    *,
    ocr_client: OCRClient | None = None,
    minimum_text_length: int = 10,
) -> TextExtractionResult:
    # Extract per-page embedded text (no OCR yet)
    embedded_pages = extract_contract_pages(pdf_path)
    embedded_text = " ".join(p.text for p in embedded_pages)

    if len(embedded_text) >= minimum_text_length:
        return TextExtractionResult(
            text=embedded_text,
            used_ocr=False,
            metadata={
                "embedded_text_length": len(embedded_text),
                "ocr_attempted": False,
            },
        )

    if ocr_client is None:
        return TextExtractionResult(
            text=embedded_text,
            used_ocr=False,
            metadata={
                "embedded_text_length": len(embedded_text),
                "ocr_attempted": False,
            },
        )

    ocr_text = _normalize_text(ocr_client.extract_text(pdf_path))
    return TextExtractionResult(
        text=ocr_text,
        used_ocr=True,
        metadata={
            "embedded_text_length": len(embedded_text),
            "ocr_attempted": True,
            "ocr_text_length": len(ocr_text),
        },
    )
