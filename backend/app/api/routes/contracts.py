from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_session
from app.api.serializers.contracts import (
    latest_contract_version,
    serialize_contract_detail,
    serialize_contract_list_item,
    serialize_contract_version_detail,
    serialize_contract_version_list,
)
from app.application.contract_upload import (
    ContractUploadError,
    upload_contract_version_file,
)
from app.application.contract_pipeline import run_contract_pipeline
from app.application.version_diff import (
    build_contract_version_comparison,
    resolve_baseline_version,
)
from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.db.models.user import User
from app.infrastructure.storage import LocalStorageService
from app.schemas.contract import (
    ContractDetailResponse,
    ContractSummaryResponse,
    ContractUpdateInput,
    ContractVersionComparisonResponse,
    ContractVersionDetailResponse,
    ContractVersionListResponse,
    PaginatedContractListResponse,
)

router = APIRouter(prefix="/api/contracts", tags=["contracts"])
ContractScope = Literal["all", "active", "history"]
logger = logging.getLogger(__name__)


class UploadContractResponse(BaseModel):
    contract_id: str
    contract_version_id: str
    version_number: int
    source: str
    used_ocr: bool
    text: str


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _contract_query():
    return select(Contract).options(
        selectinload(Contract.versions),
        selectinload(Contract.events),
    )


def _get_contract_or_404(session: Session, contract_id: str) -> Contract:
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


def _get_contract_version_or_404(
    contract: Contract, contract_version_id: str
) -> ContractVersion:
    for version in contract.versions:
        if version.id == contract_version_id:
            return version
    raise HTTPException(status_code=404, detail="Contract version not found")


def _contract_scope_filters(scope: ContractScope):
    if scope == "active":
        return (Contract.is_active.is_(True),)
    if scope == "history":
        return (
            Contract.is_active.is_(False),
            Contract.last_analyzed_at.is_not(None),
        )
    return ()


def _contract_scope_order_by(scope: ContractScope):
    if scope == "active":
        return (Contract.updated_at.desc(), Contract.created_at.desc())
    if scope == "history":
        return (Contract.last_analyzed_at.desc(), Contract.created_at.desc())
    return (Contract.created_at.desc(),)


@router.get("", response_model=PaginatedContractListResponse)
def list_contracts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    scope: ContractScope = Query("all", description="Contract scope filter"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedContractListResponse:
    """List contracts with pagination."""
    filters = _contract_scope_filters(scope)
    if current_user.role != "admin":
        filters = (*filters, Contract.owner_id == current_user.id)
    total = session.scalar(select(func.count()).select_from(Contract).where(*filters))

    offset = (page - 1) * per_page
    contracts = session.scalars(
        _contract_query()
        .where(*filters)
        .order_by(*_contract_scope_order_by(scope))
        .offset(offset)
        .limit(per_page)
    ).all()

    items = [serialize_contract_list_item(contract) for contract in contracts]
    total_pages = (total + per_page - 1) // per_page if total else 1

    return PaginatedContractListResponse(
        items=items,
        page=page,
        per_page=per_page,
        total=total or 0,
        total_pages=total_pages,
    )


@router.post(
    "/{contract_id}/versions",
    response_model=UploadContractResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_contract_version(
    contract_id: str,
    request: Request,
    source: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> UploadContractResponse:
    contract = _get_contract_or_404(session, contract_id)
    storage_service = getattr(request.app.state, "storage_service", None)
    if storage_service is None or not isinstance(storage_service, LocalStorageService):
        raise HTTPException(status_code=500, detail="Storage service not configured")

    try:
        source_enum = ContractSource(source)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid contract source") from exc

    content = await file.read()
    ocr_client = getattr(request.app.state, "ocr_client", None)

    try:
        result = upload_contract_version_file(
            session=session,
            contract=contract,
            source=source_enum,
            filename=file.filename or "contract.pdf",
            content=content,
            storage_service=storage_service,
            ocr_client=ocr_client,
        )
    except ContractUploadError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return UploadContractResponse(
        contract_id=result.contract.id,
        contract_version_id=result.contract_version.id,
        version_number=result.contract_version.version_number,
        source=result.contract_version.source.value,
        used_ocr=result.extraction.used_ocr,
        text=result.extraction.text,
    )


@router.get("/{contract_id}/versions", response_model=ContractVersionListResponse)
def list_contract_versions(
    contract_id: str,
    session: Session = Depends(get_session),
) -> ContractVersionListResponse:
    contract = _get_contract_or_404(session, contract_id)
    return serialize_contract_version_list(contract)


@router.get(
    "/{contract_id}/versions/{contract_version_id}",
    response_model=ContractVersionDetailResponse,
)
def get_contract_version_detail(
    contract_id: str,
    contract_version_id: str,
    session: Session = Depends(get_session),
) -> ContractVersionDetailResponse:
    contract = _get_contract_or_404(session, contract_id)
    contract_version = _get_contract_version_or_404(contract, contract_version_id)

    contract.last_accessed_at = _utcnow()
    session.commit()

    contract = _get_contract_or_404(session, contract_id)
    contract_version = _get_contract_version_or_404(contract, contract_version_id)
    return serialize_contract_version_detail(contract, contract_version)


@router.get("/{contract_id}", response_model=ContractDetailResponse)
def get_contract_detail(
    contract_id: str,
    session: Session = Depends(get_session),
) -> ContractDetailResponse:
    contract = _get_contract_or_404(session, contract_id)

    contract.last_accessed_at = _utcnow()
    session.commit()
    contract = _get_contract_or_404(session, contract_id)
    return serialize_contract_detail(contract)


@router.delete("/{contract_id}", status_code=204)
def delete_contract(
    contract_id: str,
    session: Session = Depends(get_session),
) -> None:
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    session.delete(contract)
    session.commit()
    return Response(status_code=204)


@router.patch("/{contract_id}", response_model=ContractDetailResponse)
def update_contract(
    contract_id: str,
    payload: ContractUpdateInput,
    session: Session = Depends(get_session),
) -> ContractDetailResponse:
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    update_data = payload.model_dump(exclude_unset=True)
    did_update = False

    if "is_active" in update_data:
        requested_is_active = update_data.pop("is_active")
        if (
            requested_is_active is not None
            and requested_is_active != contract.is_active
        ):
            if not contract.is_active and requested_is_active:
                contract.activated_at = _utcnow()
            contract.is_active = requested_is_active
            did_update = True

    if update_data:
        for key, value in update_data.items():
            setattr(contract, key, value)
        did_update = True

    if did_update:
        session.commit()

    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    return serialize_contract_detail(contract)


@router.post("/{contract_id}/analyze", response_model=ContractDetailResponse)
def analyze_contract(
    contract_id: str,
    request: Request,
    session: Session = Depends(get_session),
) -> ContractDetailResponse:
    contract = _get_contract_or_404(session, contract_id)
    latest_version = latest_contract_version(contract)
    if latest_version is None or not latest_version.text_content:
        raise HTTPException(
            status_code=422, detail="No text content available for analysis"
        )

    run_contract_pipeline(session, contract, latest_version)
    session.commit()

    if (
        latest_version is not None
        and latest_version.source == ContractSource.signed_contract
    ):
        contract.is_active = True
        contract.activated_at = _utcnow()
        session.commit()

    contract = _get_contract_or_404(session, contract_id)
    return serialize_contract_detail(contract)


@router.get("/{contract_id}/summary", response_model=ContractSummaryResponse)
def get_contract_summary(
    request: Request,
    contract_id: str,
    version_id: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> ContractSummaryResponse:
    contract = _get_contract_or_404(session, contract_id)
    selected_version = (
        _get_contract_version_or_404(contract, version_id)
        if version_id is not None
        else latest_contract_version(contract)
    )
    if selected_version is None or not selected_version.text_content:
        raise HTTPException(
            status_code=422, detail="No text content available for summary"
        )

    llm_client = getattr(request.app.state, "llm_client", None)
    if llm_client is None:
        return ContractSummaryResponse(
            summary="Resumo nao disponivel — servico de IA nao configurado.",
            key_points=[],
        )

    try:
        result = llm_client.summarize_contract(selected_version.text_content)
        return ContractSummaryResponse(
            summary=result.summary,
            key_points=result.key_points,
        )
    except Exception:
        logger.exception("Failed to generate contract summary")
        return ContractSummaryResponse(
            summary="Erro ao gerar resumo. Tente novamente mais tarde.",
            key_points=[],
        )


@router.get("/{contract_id}/compare", response_model=ContractVersionComparisonResponse)
def compare_contract_versions(
    contract_id: str,
    selected_version_id: str | None = Query(default=None),
    baseline_version_id: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> ContractVersionComparisonResponse:
    contract = _get_contract_or_404(session, contract_id)
    selected_version = (
        _get_contract_version_or_404(contract, selected_version_id)
        if selected_version_id is not None
        else latest_contract_version(contract)
    )
    if selected_version is None:
        raise HTTPException(
            status_code=422, detail="No contract versions available for comparison"
        )

    baseline_version = resolve_baseline_version(
        contract,
        selected_version=selected_version,
        baseline_version_id=baseline_version_id,
    )
    if baseline_version_id is not None and baseline_version is None:
        raise HTTPException(status_code=404, detail="Contract version not found")
    if baseline_version is not None and baseline_version.id == selected_version.id:
        baseline_version = None

    return build_contract_version_comparison(
        contract,
        selected_version=selected_version,
        baseline_version=baseline_version,
    )
