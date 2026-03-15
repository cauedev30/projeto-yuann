from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.db.models.contract import Contract
from app.schemas.contract import ContractListItem, ContractListResponse

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.get("", response_model=ContractListResponse)
def list_contracts(session: Session = Depends(get_session)) -> ContractListResponse:
    contracts = session.scalars(select(Contract).order_by(Contract.created_at.desc())).all()
    items = [
        ContractListItem(
            id=contract.id,
            title=contract.title,
            external_reference=contract.external_reference,
            status=contract.status,
        )
        for contract in contracts
    ]

    return ContractListResponse(items=items)
