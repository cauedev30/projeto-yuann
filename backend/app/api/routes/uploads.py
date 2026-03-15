from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.services.storage import LocalStorageService
from app.tasks.archive import process_signed_contract_archive
from app.tasks.ingestion import ingest_contract_version

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


class UploadContractResponse(BaseModel):
    contract_id: str
    contract_version_id: str
    source: str
    used_ocr: bool
    text: str


@router.post("/contracts", response_model=UploadContractResponse, status_code=status.HTTP_201_CREATED)
async def upload_contract(
    request: Request,
    title: str = Form(...),
    external_reference: str = Form(...),
    source: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> UploadContractResponse:
    storage_service = getattr(request.app.state, "storage_service", None)
    if storage_service is None or not isinstance(storage_service, LocalStorageService):
        raise HTTPException(status_code=500, detail="Storage service not configured")

    try:
        source_enum = ContractSource(source)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid contract source") from exc

    contract = session.scalar(select(Contract).where(Contract.external_reference == external_reference))
    if contract is None:
        contract = Contract(title=title, external_reference=external_reference, status="uploaded")
        session.add(contract)
        session.flush()
    else:
        contract.title = title

    content = await file.read()
    storage_key = storage_service.store_bytes(file.filename or "contract.pdf", content)

    contract_version = ContractVersion(
        contract=contract,
        source=source_enum,
        original_filename=file.filename or "contract.pdf",
        storage_key=storage_key,
    )
    session.add(contract_version)
    session.commit()
    session.refresh(contract_version)

    ocr_client = getattr(request.app.state, "ocr_client", None)
    extraction_result = ingest_contract_version(
        session,
        contract_version,
        storage_service=storage_service,
        ocr_client=ocr_client,
    )

    if contract_version.source == ContractSource.signed_contract:
        process_signed_contract_archive(session, contract_version=contract_version)

    return UploadContractResponse(
        contract_id=contract.id,
        contract_version_id=contract_version.id,
        source=contract_version.source.value,
        used_ocr=extraction_result.used_ocr,
        text=extraction_result.text,
    )
