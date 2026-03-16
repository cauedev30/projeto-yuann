from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_session
from app.api.serializers.contracts import serialize_contract_detail, serialize_contract_list_item
from app.db.models.analysis import ContractAnalysis
from app.db.models.contract import Contract
from app.schemas.contract import ContractDetailResponse, ContractListResponse

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


def _contract_query():
    return select(Contract).options(
        selectinload(Contract.versions),
        selectinload(Contract.analyses).selectinload(ContractAnalysis.findings),
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
