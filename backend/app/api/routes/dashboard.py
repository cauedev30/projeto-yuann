from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_session
from app.application.dashboard import build_dashboard_snapshot
from app.db.models.user import User
from app.schemas.dashboard import DashboardSnapshotResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSnapshotResponse)
def get_dashboard_snapshot(
    today: date | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DashboardSnapshotResponse:
    return build_dashboard_snapshot(
        session=session, today=today or date.today(), current_user=current_user
    )
