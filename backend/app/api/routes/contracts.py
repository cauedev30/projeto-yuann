from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncGenerator, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel

from app.api.dependencies import get_session
from app.api.serializers.contracts import (
    latest_contract_version,
    latest_version_analysis,
    serialize_contract_detail,
    serialize_contract_list_item,
    serialize_contract_version_detail,
    serialize_contract_version_list,
)
from app.application.analysis import mark_contract_analysis_completed
from app.application.contract_upload import ContractUploadError, upload_contract_version_file
from app.application.contract_pipeline import run_contract_pipeline
from app.application.version_diff import (
    build_contract_version_comparison,
    resolve_baseline_version,
)
from app.db.models.analysis import ContractAnalysis
from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.domain.playbook import PLAYBOOK_CLAUSES
from app.infrastructure.contract_chunker import chunk_contract
from app.infrastructure.docx_generator import generate_corrected_contract_docx
from app.infrastructure.storage import LocalStorageService
from app.schemas.contract import (
    ContractDetailResponse,
    ContractSummaryResponse,
    ContractUpdateInput,
    CorrectedContractResponse,
    ContractVersionComparisonResponse,
    ContractVersionDetailResponse,
    ContractVersionListResponse,
    PaginatedContractListResponse,
)

router = APIRouter(prefix="/api/contracts", tags=["contracts"])
ContractScope = Literal["all", "active", "history"]


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
        selectinload(Contract.versions)
        .selectinload(ContractVersion.analyses)
        .selectinload(ContractAnalysis.findings),
        selectinload(Contract.events),
    )


def _get_contract_or_404(session: Session, contract_id: str) -> Contract:
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


def _get_contract_version_or_404(contract: Contract, contract_version_id: str) -> ContractVersion:
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
) -> PaginatedContractListResponse:
    """List contracts with pagination."""
    filters = _contract_scope_filters(scope)
    total = session.scalar(
        select(func.count()).select_from(Contract).where(*filters)
    )

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
    llm_client = getattr(request.app.state, "llm_client", None)

    try:
        result = upload_contract_version_file(
            session=session,
            contract=contract,
            source=source_enum,
            filename=file.filename or "contract.pdf",
            content=content,
            storage_service=storage_service,
            ocr_client=ocr_client,
            llm_client=llm_client,
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
        if requested_is_active is not None and requested_is_active != contract.is_active:
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
        raise HTTPException(status_code=422, detail="No text content available for analysis")

    llm_client = getattr(request.app.state, "llm_client", None)
    run_contract_pipeline(session, contract, latest_version, llm_client=llm_client)
    session.commit()

    contract = _get_contract_or_404(session, contract_id)
    return serialize_contract_detail(contract)


@router.get("/{contract_id}/summary", response_model=ContractSummaryResponse)
def get_contract_summary(
    contract_id: str,
    request: Request,
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
        raise HTTPException(status_code=422, detail="No text content available for summary")

    llm_client = getattr(request.app.state, "llm_client", None)
    if llm_client is None:
        return ContractSummaryResponse(
            summary="Resumo nao disponivel — servico de IA nao configurado.",
            key_points=[],
        )

    result = llm_client.summarize_contract(text=selected_version.text_content)
    return ContractSummaryResponse(
        summary=result.summary,
        key_points=result.key_points,
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
        raise HTTPException(status_code=422, detail="No contract versions available for comparison")

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


async def _analysis_stream(
    contract_id: str,
    contract_version_id: str,
    contract_text: str,
    llm_client,
    session_factory,
) -> AsyncGenerator[str, None]:
    """Generate SSE events for contract analysis progress."""
    yield f"data: {json.dumps({'stage': 'started', 'message': 'Iniciando análise...'})}\n\n"
    await asyncio.sleep(0.1)
    
    # Chunk the contract
    yield f"data: {json.dumps({'stage': 'chunking', 'message': 'Dividindo contrato em cláusulas...'})}\n\n"
    chunks = chunk_contract(contract_text)
    chunk_texts = [c.content for c in chunks]
    total_chunks = len(chunks)
    await asyncio.sleep(0.1)
    
    yield f"data: {json.dumps({'stage': 'analyzing', 'message': f'Analisando {total_chunks} seções...', 'total': total_chunks})}\n\n"
    
    # Call Gemini for analysis
    try:
        result = llm_client.analyze_contract(
            chunks=chunk_texts,
            playbook=list(PLAYBOOK_CLAUSES),
        )
        
        # Save to database
        from sqlalchemy.orm import Session as DBSession
        from app.db.models.analysis import AnalysisStatus, ContractAnalysis, ContractAnalysisFinding
        from app.db.models.contract import Contract
        from app.db.models.policy import Policy
        
        with session_factory() as session:
            contract = session.scalar(select(Contract).where(Contract.id == contract_id))
            policy = session.scalar(select(Policy).order_by(Policy.created_at.desc()))
            
            if contract:
                analysis = ContractAnalysis(
                    contract_id=contract.id,
                    contract_version_id=contract_version_id,
                    policy_version=policy.version if policy else "v1.0",
                    status=AnalysisStatus.completed,
                    contract_risk_score=result.contract_risk_score,
                    raw_payload={
                        "items": [item.model_dump() for item in result.items],
                        "summary": result.summary,
                    },
                    findings=[
                        ContractAnalysisFinding(
                            clause_name=item.clause_code,
                            status="evaluated",
                            severity=item.severity,
                            current_summary=item.explanation,
                            policy_rule=item.clause_code,
                            risk_explanation=item.explanation,
                            suggested_adjustment_direction=item.suggested_correction,
                            metadata_json={
                                "risk_score": item.risk_score,
                                "playbook_title": item.clause_title,
                            },
                        )
                        for item in result.items
                    ],
                )
                session.add(analysis)
                mark_contract_analysis_completed(contract)
                contract.status = "analisado"
                session.commit()
        
        yield f"data: {json.dumps({'stage': 'completed', 'message': 'Análise concluída!', 'risk_score': result.contract_risk_score, 'findings_count': len(result.items)})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'stage': 'error', 'message': f'Erro na análise: {str(e)}'})}\n\n"


@router.post("/{contract_id}/analyze-stream")
async def analyze_contract_stream(
    contract_id: str,
    request: Request,
    session: Session = Depends(get_session),
):
    """Analyze contract with SSE streaming progress updates."""
    contract = _get_contract_or_404(session, contract_id)
    latest_version = latest_contract_version(contract)
    if latest_version is None or not latest_version.text_content:
        raise HTTPException(status_code=422, detail="No text content available for analysis")

    llm_client = getattr(request.app.state, "llm_client", None)
    if llm_client is None:
        raise HTTPException(status_code=503, detail="LLM service not configured")

    return StreamingResponse(
        _analysis_stream(
            contract_id=contract_id,
            contract_version_id=latest_version.id,
            contract_text=latest_version.text_content,
            llm_client=llm_client,
            session_factory=request.app.state.session_factory,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/{contract_id}/generate-corrected", response_model=CorrectedContractResponse)
def generate_corrected_contract(
    contract_id: str,
    request: Request,
    session: Session = Depends(get_session),
) -> CorrectedContractResponse:
    """Generate a corrected version of the contract based on analysis findings.
    
    Saves the result to the database for fast download later.
    """
    contract = _get_contract_or_404(session, contract_id)
    latest_version = latest_contract_version(contract)
    if latest_version is None or not latest_version.text_content:
        raise HTTPException(status_code=422, detail="No text content available")

    latest_analysis = latest_version_analysis(latest_version)
    if latest_analysis is None:
        raise HTTPException(status_code=422, detail="No analysis available. Run analysis first.")

    # Check if we already have a corrected version for this analysis
    if latest_analysis.corrected_text:
        corrections = latest_analysis.corrections_summary or []
        return CorrectedContractResponse(
            corrected_text=latest_analysis.corrected_text,
            corrections=corrections,
        )

    llm_client = getattr(request.app.state, "llm_client", None)
    if llm_client is None:
        raise HTTPException(status_code=503, detail="LLM service not configured")

    # Filter only critical/attention findings
    findings_list = [
        {
            "clause_code": f.clause_name,
            "severity": f.severity,
            "explanation": f.risk_explanation,
            "suggested_correction": f.suggested_adjustment_direction,
        }
        for f in latest_analysis.findings
        if f.severity.lower() in ("critical", "attention", "high", "medium")
    ]

    if not findings_list:
        # No corrections needed - return original
        return CorrectedContractResponse(
            corrected_text=latest_version.text_content,
            corrections=[],
        )

    result = llm_client.generate_corrected_contract(
        original=latest_version.text_content,
        findings=findings_list,
        playbook=list(PLAYBOOK_CLAUSES),
    )

    corrections_list = [
        {
            "clause_name": c.clause_name,
            "original_text": c.original_text,
            "corrected_text": c.corrected_text,
            "reason": c.reason,
        }
        for c in result.corrections
    ]

    # Save to database for fast download later
    latest_analysis.corrected_text = result.corrected_text
    latest_analysis.corrections_summary = corrections_list
    session.commit()

    return CorrectedContractResponse(
        corrected_text=result.corrected_text,
        corrections=corrections_list,
    )


@router.get("/{contract_id}/download-corrected")
def download_corrected_contract_docx(
    contract_id: str,
    session: Session = Depends(get_session),
):
    """Download corrected contract as DOCX file.
    
    Requires generate-corrected to be called first. Downloads are instant
    since the corrected text is retrieved from the database.
    """
    contract = _get_contract_or_404(session, contract_id)
    latest_analysis = latest_version_analysis(latest_contract_version(contract))
    if latest_analysis is None:
        raise HTTPException(status_code=422, detail="No analysis available. Run analysis first.")

    # Check if corrected version exists in DB
    if not latest_analysis.corrected_text:
        raise HTTPException(
            status_code=422, 
            detail="Corrected contract not generated yet. Click 'Gerar Contrato Corrigido' first."
        )

    # Build a simple result object for docx generator
    from app.infrastructure.gemini_models import CorrectedContractResult, CorrectionItem
    
    corrections = latest_analysis.corrections_summary or []
    result = CorrectedContractResult(
        corrected_text=latest_analysis.corrected_text,
        corrections=[
            CorrectionItem(
                clause_name=c.get("clause_name", ""),
                original_text=c.get("original_text", ""),
                corrected_text=c.get("corrected_text", ""),
                reason=c.get("reason", ""),
            )
            for c in corrections
        ],
    )

    docx_buffer = generate_corrected_contract_docx(
        result=result,
        contract_title=contract.title or "Contrato Corrigido",
    )

    filename = f"contrato-corrigido-{contract_id[:8]}.docx"
    
    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
