from __future__ import annotations

from pathlib import Path
from typing import Protocol


class OCRClient(Protocol):
    def extract_text(self, pdf_path: Path) -> str: ...


class NoopOcrClient:
    def extract_text(self, pdf_path: Path) -> str:
        return ""
