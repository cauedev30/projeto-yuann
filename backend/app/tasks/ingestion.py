from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models.contract import ContractVersion
from app.infrastructure.ocr import OCRClient
from app.infrastructure.pdf_text import TextExtractionResult, extract_contract_text
from app.infrastructure.storage import LocalStorageService


def _build_ingestion_tmp_root() -> Path:
    root = Path(__file__).resolve().parents[3] / "tmp" / "backend-ingestion"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _build_ingestion_workspace() -> Path:
    workspace = _build_ingestion_tmp_root() / str(uuid4())
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def ingest_contract_version(
    session: Session,
    contract_version: ContractVersion,
    *,
    storage_service: LocalStorageService,
    ocr_client: OCRClient | None = None,
) -> TextExtractionResult:
    file_bytes = storage_service.read_bytes(contract_version.storage_key)

    pdf_path = _build_ingestion_workspace() / contract_version.original_filename
    pdf_path.write_bytes(file_bytes)
    result = extract_contract_text(pdf_path, ocr_client=ocr_client)

    contract_version.text_content = result.text
    contract_version.extraction_metadata = result.metadata
    session.add(contract_version)
    session.flush()

    return result
