from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.contract_pipeline import run_contract_pipeline, run_policy_analysis
from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.infrastructure.pdf_text import TextExtractionError
from app.infrastructure.ocr import OCRClient
from app.infrastructure.storage import LocalStorageService
from app.tasks.archive import process_signed_contract_archive
from app.tasks.ingestion import TextExtractionResult, ingest_contract_version


class ContractUploadError(Exception):
    pass


@dataclass(slots=True)
class ContractUploadResult:
    contract: Contract
    contract_version: ContractVersion
    extraction: TextExtractionResult


def upload_contract_file(
    *,
    session: Session,
    title: str,
    external_reference: str,
    source: ContractSource,
    filename: str,
    content: bytes,
    storage_service: LocalStorageService,
    ocr_client: OCRClient | None = None,
    llm_client: object | None = None,
) -> ContractUploadResult:
    contract = session.scalar(select(Contract).where(Contract.external_reference == external_reference))
    if contract is None:
        contract = Contract(title=title, external_reference=external_reference, status="enviado")
        session.add(contract)
    else:
        contract.title = title

    storage_key = storage_service.store_bytes(filename, content)
    contract_version = ContractVersion(
        contract=contract,
        source=source,
        original_filename=filename,
        storage_key=storage_key,
    )
    session.add(contract_version)

    try:
        session.flush()
        extraction = ingest_contract_version(
            session,
            contract_version,
            storage_service=storage_service,
            ocr_client=ocr_client,
        )

        if contract_version.source == ContractSource.signed_contract:
            process_signed_contract_archive(session, contract_version=contract_version)
            run_policy_analysis(
                session, contract, contract_version.text_content or "",
                llm_client=llm_client,
            )
        else:
            run_contract_pipeline(
                session, contract, contract_version, llm_client=llm_client,
            )
        session.commit()
    except TextExtractionError as exc:
        session.rollback()
        storage_service.delete(storage_key)
        raise ContractUploadError("Uploaded file is not a readable PDF") from exc
    except Exception:
        session.rollback()
        storage_service.delete(storage_key)
        raise

    session.refresh(contract)
    session.refresh(contract_version)

    return ContractUploadResult(
        contract=contract,
        contract_version=contract_version,
        extraction=extraction,
    )
