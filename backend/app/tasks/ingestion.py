from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy.orm import Session

from app.db.models.contract import ContractVersion
from app.services.ocr import OCRClient
from app.services.pdf_text import TextExtractionResult, extract_contract_text
from app.services.storage import LocalStorageService


def ingest_contract_version(
    session: Session,
    contract_version: ContractVersion,
    *,
    storage_service: LocalStorageService,
    ocr_client: OCRClient | None = None,
) -> TextExtractionResult:
    file_bytes = storage_service.read_bytes(contract_version.storage_key)

    with TemporaryDirectory() as temp_dir:
        pdf_path = Path(temp_dir) / contract_version.original_filename
        pdf_path.write_bytes(file_bytes)
        result = extract_contract_text(pdf_path, ocr_client=ocr_client)

    contract_version.text_content = result.text
    contract_version.extraction_metadata = result.metadata
    session.add(contract_version)
    session.commit()
    session.refresh(contract_version)

    return result
