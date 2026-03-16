from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz

from app.infrastructure.ocr import OCRClient


class TextExtractionError(Exception):
    pass


@dataclass(slots=True)
class TextExtractionResult:
    text: str
    used_ocr: bool
    metadata: dict[str, object]


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def extract_contract_text(
    pdf_path: Path,
    *,
    ocr_client: OCRClient | None = None,
    minimum_text_length: int = 10,
) -> TextExtractionResult:
    try:
        with fitz.open(pdf_path) as document:
            embedded_text = _normalize_text(" ".join(page.get_text("text") for page in document))
    except fitz.FileDataError as exc:
        raise TextExtractionError("Uploaded file is not a readable PDF") from exc

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
