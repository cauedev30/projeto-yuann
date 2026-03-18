from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.auth import router as auth_router
from app.api.routes.contracts import router as contracts_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.policies import router as policies_router
from app.api.routes.uploads import router as uploads_router
from app.db.base import Base
from app.db.models.policy import Policy, PolicyRule
from app.infrastructure.notifications import NoopEmailSender, SmtpEmailSender
from app.infrastructure.ocr import NoopOcrClient
from app.infrastructure.storage import LocalStorageService


def _seed_default_policy(session: Session) -> None:
    existing = session.scalar(select(Policy).where(Policy.version == "v1.0"))
    if existing is not None:
        return

    policy = Policy(name="Politica Padrao Yuann", version="v1.0")
    session.add(policy)
    session.flush()

    rules = [
        PolicyRule(policy_id=policy.id, code="MIN_TERM_MONTHS", value=48, description="Prazo minimo de vigencia: 48 meses"),
        PolicyRule(policy_id=policy.id, code="MAX_TERM_MONTHS", value=60, description="Prazo maximo de vigencia: 60 meses"),
        PolicyRule(policy_id=policy.id, code="MAX_FINE_MONTHS", value=3, description="Multa maxima: 3 alugueis"),
        PolicyRule(policy_id=policy.id, code="MAX_VALUE", value=3000, description="Valor maximo do contrato: R$ 3.000"),
        PolicyRule(policy_id=policy.id, code="GRACE_PERIOD_DAYS", value=[0, 30, 60, 90], description="Periodos de carencia permitidos (dias)"),
    ]
    session.add_all(rules)
    session.commit()


def create_app(
    *,
    database_url: str = "sqlite:///./legaltech.db",
    storage_directory: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="LegalTech MVP API")
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(127\.0\.0\.1|localhost):\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    )
    app.state.session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        _seed_default_policy(session)

    app.include_router(auth_router)
    app.include_router(policies_router)
    app.include_router(contracts_router)
    app.include_router(uploads_router)
    app.include_router(notifications_router)
    app.include_router(dashboard_router)
    app.state.storage_service = LocalStorageService(
        storage_directory or Path(__file__).resolve().parents[2] / "uploads",
    )
    app.state.ocr_client = NoopOcrClient()

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        from app.infrastructure.openai_client import OpenAIAnalysisClient

        app.state.llm_client = OpenAIAnalysisClient(api_key=openai_api_key)
    else:
        app.state.llm_client = None

    smtp_host = os.environ.get("MAILPIT_SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("MAILPIT_SMTP_PORT", "1025"))
    if os.environ.get("SMTP_ENABLED", "").lower() in ("1", "true"):
        app.state.email_sender = SmtpEmailSender(host=smtp_host, port=smtp_port)
    else:
        app.state.email_sender = NoopEmailSender()

    jwt_secret = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
    app.state.jwt_secret = jwt_secret
    app.state.jwt_expiration_minutes = int(os.environ.get("JWT_EXPIRATION_MINUTES", "480"))

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app
