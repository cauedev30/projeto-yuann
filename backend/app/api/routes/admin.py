from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session, require_admin, get_current_user
from app.db.models.user import User
from app.domain.auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])

class UserCreateInput(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "user"

class UserListResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool

class AssignContractInput(BaseModel):
    contract_id: str
    user_id: str

@router.get("/users", response_model=list[UserListResponse])
def list_users(
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> list[UserListResponse]:
    users = session.scalars(select(User)).all()
    return [
        UserListResponse(id=u.id, email=u.email, full_name=u.full_name, role=u.role, is_active=u.is_active)
        for u in users
    ]

@router.post("/users", response_model=UserListResponse, status_code=201)
def create_user(
    payload: UserCreateInput,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> UserListResponse:
    existing = session.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserListResponse(
        id=user.id, email=user.email, full_name=user.full_name, role=user.role, is_active=user.is_active
    )

@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    payload: dict,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> dict:
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if "role" in payload:
        user.role = payload["role"]
    if "is_active" in payload:
        user.is_active = payload["is_active"]
    session.commit()
    return {"id": user.id, "role": user.role, "is_active": user.is_active}

@router.post("/assign-contract")
def assign_contract(
    payload: AssignContractInput,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> dict:
    from app.db.models.contract import Contract
    contract = session.scalar(select(Contract).where(Contract.id == payload.contract_id))
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    user = session.scalar(select(User).where(User.id == payload.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    contract.owner_id = payload.user_id
    session.commit()
    return {"contract_id": contract.id, "owner_id": contract.owner_id}
