from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_session
from app.api.serializers.contracts import serialize_contract_detail, serialize_contract_list_item
from app.application.contract_pipeline import run_contract_pipeline
from app.db.models.analysis import ContractAnalysis
from app.db.models.contract import Contract
from app.domain.playbook import PLAYBOOK_CLAUSES
from app.infrastructure.contract_chunker import chunk_contract
from app.infrastructure.docx_generator import generate_corrected_contract_docx
from app.schemas.contract import (
    ContractDetailResponse,
    ContractListResponse,
    ContractSummaryResponse,
    ContractUpdateInput,
    CorrectedContractResponse,
    PaginatedContractListResponse,
)

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


def _contract_query():
    return select(Contract).options(
        selectinload(Contract.versions),
        selectinload(Contract.analyses).selectinload(ContractAnalysis.findings),
        selectinload(Contract.events),
    )


@router.get("", response_model=PaginatedContractListResponse)
def list_contracts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session),
) -> PaginatedContractListResponse:
    """List contracts with pagination."""
    total = session.scalar(select(func.count()).select_from(Contract))
    
    offset = (page - 1) * per_page
    contracts = session.scalars(
        _contract_query()
        .order_by(Contract.created_at.desc())
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


@router.get("/{contract_id}", response_model=ContractDetailResponse)
def get_contract_detail(
    contract_id: str,
    session: Session = Depends(get_session),
) -> ContractDetailResponse:
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

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
    if update_data:
        for key, value in update_data.items():
            setattr(contract, key, value)
        session.commit()
        
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    return serialize_contract_detail(contract)


@router.post("/{contract_id}/analyze", response_model=ContractDetailResponse)
def analyze_contract(
    contract_id: str,
    request: Request,
    session: Session = Depends(get_session),
) -> ContractDetailResponse:
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    latest_version = (
        max(contract.versions, key=lambda v: (v.created_at, v.id))
        if contract.versions
        else None
    )
    if latest_version is None or not latest_version.text_content:
        raise HTTPException(status_code=422, detail="No text content available for analysis")

    llm_client = getattr(request.app.state, "llm_client", None)
    run_contract_pipeline(session, contract, latest_version, llm_client=llm_client)
    session.commit()

    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    return serialize_contract_detail(contract)


@router.get("/{contract_id}/summary", response_model=ContractSummaryResponse)
def get_contract_summary(
    contract_id: str,
    request: Request,
    session: Session = Depends(get_session),
) -> ContractSummaryResponse:
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    latest_version = (
        max(contract.versions, key=lambda v: (v.created_at, v.id))
        if contract.versions
        else None
    )
    if latest_version is None or not latest_version.text_content:
        raise HTTPException(status_code=422, detail="No text content available for summary")

    llm_client = getattr(request.app.state, "llm_client", None)
    if llm_client is None:
        return ContractSummaryResponse(
            summary="Resumo nao disponivel — servico de IA nao configurado.",
            key_points=[],
        )

    result = llm_client.summarize_contract(text=latest_version.text_content)
    return ContractSummaryResponse(
        summary=result.summary,
        key_points=result.key_points,
    )


async def _analysis_stream(
    contract_id: str,
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
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    latest_version = (
        max(contract.versions, key=lambda v: (v.created_at, v.id))
        if contract.versions
        else None
    )
    if latest_version is None or not latest_version.text_content:
        raise HTTPException(status_code=422, detail="No text content available for analysis")

    llm_client = getattr(request.app.state, "llm_client", None)
    if llm_client is None:
        raise HTTPException(status_code=503, detail="LLM service not configured")

    return StreamingResponse(
        _analysis_stream(
            contract_id=contract_id,
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
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    latest_version = (
        max(contract.versions, key=lambda v: (v.created_at, v.id))
        if contract.versions
        else None
    )
    if latest_version is None or not latest_version.text_content:
        raise HTTPException(status_code=422, detail="No text content available")

    # Get latest analysis
    latest_analysis = (
        max(contract.analyses, key=lambda a: (a.created_at, a.id))
        if contract.analyses
        else None
    )
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
    contract = session.scalar(_contract_query().where(Contract.id == contract_id))
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    latest_analysis = (
        max(contract.analyses, key=lambda a: (a.created_at, a.id))
        if contract.analyses
        else None
    )
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
