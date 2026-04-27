from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_session, require_admin
from app.db.models.user import User
from app.domain.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterInput(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "user"


class LoginInput(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    role: str


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    payload: RegisterInput,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
) -> AuthResponse:
    existing = session.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
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

    jwt_secret = getattr(request.app.state, "jwt_secret", "dev-secret")
    jwt_exp = getattr(request.app.state, "jwt_expiration_minutes", 480)
    token = create_access_token(user_id=user.id, secret=jwt_secret, expires_minutes=jwt_exp)

    return AuthResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginInput,
    request: Request,
    session: Session = Depends(get_session),
) -> AuthResponse:
    user = session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    jwt_secret = getattr(request.app.state, "jwt_secret", "dev-secret")
    jwt_exp = getattr(request.app.state, "jwt_expiration_minutes", 480)
    token = create_access_token(user_id=user.id, secret=jwt_secret, expires_minutes=jwt_exp)

    return AuthResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        role=current_user.role,
    )
