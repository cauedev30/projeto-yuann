from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env file from backend directory
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
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
from app.db.models import Policy, PolicyRule
from app.infrastructure.openai_client import OpenAIAnalysisClient
from app.infrastructure.notifications import NoopEmailSender, SmtpEmailSender
from app.infrastructure.ocr import NoopOcrClient
from app.infrastructure.storage import LocalStorageService


def _get_database_url(database_url: str | None) -> str:
    resolved_database_url = database_url or os.environ.get(
        "DATABASE_URL",
        "sqlite:///./legaltech.db",
    )

    if resolved_database_url.startswith("postgresql://"):
        return resolved_database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    if resolved_database_url.startswith("postgres://"):
        return resolved_database_url.replace("postgres://", "postgresql+psycopg://", 1)

    return resolved_database_url


def _get_storage_directory(storage_directory: Path | None) -> Path:
    if storage_directory is not None:
        return storage_directory

    upload_dir = os.environ.get("UPLOAD_DIR")
    if upload_dir:
        return Path(upload_dir)

    return Path(__file__).resolve().parents[2] / "uploads"


def _get_cors_origins(cors_origins: list[str] | None) -> list[str]:
    if cors_origins is not None:
        return cors_origins

    configured_origins = os.environ.get("CORS_ORIGINS", "")
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]


def _seed_default_policy(session: Session) -> None:
    existing = session.scalar(select(Policy).where(Policy.version == "v1.0"))
    if existing is not None:
        return

    policy = Policy(name="Politica Padrao LegalBoard", version="v1.0")
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
    database_url: str | None = None,
    storage_directory: Path | None = None,
    cors_origins: list[str] | None = None,
) -> FastAPI:
    resolved_database_url = _get_database_url(database_url)
    resolved_storage_directory = _get_storage_directory(storage_directory)
    resolved_cors_origins = _get_cors_origins(cors_origins)

    app = FastAPI(title="LegalBoard API")
    cors_kwargs: dict[str, object] = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if resolved_cors_origins:
        cors_kwargs["allow_origins"] = resolved_cors_origins
    else:
        cors_kwargs["allow_origin_regex"] = r"http://(127\.0\.0\.1|localhost):\d+"
    app.add_middleware(CORSMiddleware, **cors_kwargs)

    engine = create_engine(
        resolved_database_url,
        connect_args={"check_same_thread": False} if resolved_database_url.startswith("sqlite") else {},
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
    app.state.storage_service = LocalStorageService(resolved_storage_directory)
    app.state.ocr_client = NoopOcrClient()

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

    if openai_api_key:
        app.state.llm_client = OpenAIAnalysisClient(
            api_key=openai_api_key,
            model=openai_model,
        )
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
