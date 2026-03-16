from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.contract_upload import upload_contract_file
from app.api.dependencies import get_session
from app.db.models.contract import ContractSource
from app.infrastructure.storage import LocalStorageService

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

    content = await file.read()
    ocr_client = getattr(request.app.state, "ocr_client", None)
    result = upload_contract_file(
        session=session,
        title=title,
        external_reference=external_reference,
        source=source_enum,
        filename=file.filename or "contract.pdf",
        content=content,
        storage_service=storage_service,
        ocr_client=ocr_client,
    )

    return UploadContractResponse(
        contract_id=result.contract.id,
        contract_version_id=result.contract_version.id,
        source=result.contract_version.source.value,
        used_ocr=result.extraction.used_ocr,
        text=result.extraction.text,
    )
