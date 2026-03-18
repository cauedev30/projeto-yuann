from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_session
from app.api.serializers.contracts import serialize_contract_detail, serialize_contract_list_item
from app.application.contract_pipeline import run_contract_pipeline
from app.db.models.analysis import ContractAnalysis
from app.db.models.contract import Contract
from app.schemas.contract import ContractDetailResponse, ContractListResponse, ContractSummaryResponse, ContractUpdateInput

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


def _contract_query():
    return select(Contract).options(
        selectinload(Contract.versions),
        selectinload(Contract.analyses).selectinload(ContractAnalysis.findings),
        selectinload(Contract.events),
    )


@router.get("", response_model=ContractListResponse)
def list_contracts(session: Session = Depends(get_session)) -> ContractListResponse:
    contracts = session.scalars(_contract_query().order_by(Contract.created_at.desc())).all()
    items = [serialize_contract_list_item(contract) for contract in contracts]
    return ContractListResponse(items=items)


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

    result = llm_client.summarize_contract(contract_text=latest_version.text_content)
    return ContractSummaryResponse(
        summary=result.get("summary", ""),
        key_points=result.get("key_points", []),
    )
