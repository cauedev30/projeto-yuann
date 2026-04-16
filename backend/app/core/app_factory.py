from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env file from backend directory
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.auth import router as auth_router
from app.api.routes.contracts import router as contracts_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.policies import router as policies_router
from app.api.routes.search import router as search_router
from app.api.routes.uploads import router as uploads_router
from app.db.base import Base
from app.db.models import Policy, PolicyRule
from app.core.database_url import resolve_database_url
from app.infrastructure.openai_client import OpenAIAnalysisClient
from app.infrastructure.notifications import NoopEmailSender, SmtpEmailSender
from app.infrastructure.ocr import NoopOcrClient
from app.infrastructure.storage import LocalStorageService
from app.infrastructure.embeddings import EmbeddingClient

_embedding_client: EmbeddingClient | None = None


def get_embedding_client() -> EmbeddingClient | None:
    return _embedding_client


def _get_database_url(database_url: str | None) -> str:
    return resolve_database_url(
        database_url,
        env_database_url=os.environ.get("DATABASE_URL"),
        local_default="sqlite:///./legaltech.db",
    )


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
    return [
        origin.strip() for origin in configured_origins.split(",") if origin.strip()
    ]


def _seed_default_policy(session: Session) -> None:
    existing = session.scalar(select(Policy).where(Policy.version == "v1.0"))
    if existing is not None:
        return

    policy = Policy(name="Politica Padrao LegalBoard", version="v1.0")
    session.add(policy)
    session.flush()

    rules = [
        PolicyRule(
            policy_id=policy.id,
            code="MIN_TERM_MONTHS",
            value=48,
            description="Prazo minimo de vigencia: 48 meses",
        ),
        PolicyRule(
            policy_id=policy.id,
            code="MAX_TERM_MONTHS",
            value=60,
            description="Prazo maximo de vigencia: 60 meses",
        ),
        PolicyRule(
            policy_id=policy.id,
            code="MAX_FINE_MONTHS",
            value=3,
            description="Multa maxima: 3 alugueis",
        ),
        PolicyRule(
            policy_id=policy.id,
            code="MAX_VALUE",
            value=3000,
            description="Valor maximo do contrato: R$ 3.000",
        ),
        PolicyRule(
            policy_id=policy.id,
            code="GRACE_PERIOD_DAYS",
            value=[0, 30, 60, 90],
            description="Periodos de carencia permitidos (dias)",
        ),
    ]
    session.add_all(rules)
    session.commit()


def _json_column_type(dialect_name: str) -> str:
    return "JSONB" if dialect_name == "postgresql" else "JSON"


def _timestamp_column_type(dialect_name: str) -> str:
    return "TIMESTAMP WITH TIME ZONE" if dialect_name == "postgresql" else "DATETIME"


def _reconcile_legacy_schema(engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    dialect_name = engine.dialect.name
    json_type = _json_column_type(dialect_name)
    timestamp_type = _timestamp_column_type(dialect_name)
    false_literal = "false" if dialect_name == "postgresql" else "0"

    def add_missing_columns(
        table_name: str, definitions: list[tuple[str, str]]
    ) -> None:
        if table_name not in table_names:
            return

        existing_columns = {
            column["name"] for column in inspector.get_columns(table_name)
        }
        statements = [
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            for column_name, column_definition in definitions
            if column_name not in existing_columns
        ]
        if not statements:
            return

        with engine.begin() as connection:
            for statement in statements:
                connection.exec_driver_sql(statement)

    add_missing_columns(
        "contracts",
        [
            ("signature_date", "DATE"),
            ("start_date", "DATE"),
            ("end_date", "DATE"),
            ("term_months", "INTEGER"),
            ("financial_terms", json_type),
            ("is_active", f"BOOLEAN NOT NULL DEFAULT {false_literal}"),
            ("activated_at", timestamp_type),
            ("last_accessed_at", timestamp_type),
            ("last_analyzed_at", timestamp_type),
        ],
    )
    add_missing_columns(
        "contract_versions",
        [
            ("extraction_metadata", json_type),
            ("version_number", "INTEGER"),
        ],
    )
    add_missing_columns(
        "contract_analyses",
        [
            ("contract_version_id", "VARCHAR(36)"),
            ("corrected_text", "TEXT"),
            ("corrections_summary", json_type),
        ],
    )
    add_missing_columns(
        "notifications",
        [
            ("dismissed_at", timestamp_type),
        ],
    )

    if "contract_versions" in table_names:
        with engine.begin() as connection:
            version_rows = (
                connection.execute(
                    text(
                        """
                    SELECT id, contract_id, created_at
                    FROM contract_versions
                    ORDER BY contract_id, created_at, id
                    """
                    )
                )
                .mappings()
                .all()
            )
            current_numbers: dict[str, int] = {}
            for row in version_rows:
                contract_id = str(row["contract_id"])
                current_numbers[contract_id] = current_numbers.get(contract_id, 0) + 1
                connection.execute(
                    text(
                        """
                        UPDATE contract_versions
                        SET version_number = :version_number
                        WHERE id = :version_id AND version_number IS NULL
                        """
                    ),
                    {
                        "version_number": current_numbers[contract_id],
                        "version_id": row["id"],
                    },
                )

    if "contract_versions" in table_names and "contract_analyses" in table_names:
        with engine.begin() as connection:
            version_rows = (
                connection.execute(
                    text(
                        """
                    SELECT id, contract_id, created_at
                    FROM contract_versions
                    ORDER BY contract_id, created_at, id
                    """
                    )
                )
                .mappings()
                .all()
            )
            versions_by_contract: dict[str, list[dict[str, object]]] = {}
            for row in version_rows:
                contract_id = str(row["contract_id"])
                versions_by_contract.setdefault(contract_id, []).append(
                    {
                        "id": row["id"],
                        "created_at": row["created_at"],
                    }
                )

            analysis_rows = (
                connection.execute(
                    text(
                        """
                    SELECT id, contract_id, created_at
                    FROM contract_analyses
                    WHERE contract_id IS NOT NULL
                    ORDER BY contract_id, created_at, id
                    """
                    )
                )
                .mappings()
                .all()
            )
            for row in analysis_rows:
                contract_id = str(row["contract_id"])
                versions = versions_by_contract.get(contract_id, [])
                if not versions:
                    continue
                matching_versions = [
                    version
                    for version in versions
                    if row["created_at"] is None
                    or version["created_at"] is None
                    or version["created_at"] <= row["created_at"]
                ]
                chosen_version = (
                    matching_versions[-1] if matching_versions else versions[-1]
                )
                connection.execute(
                    text(
                        """
                        UPDATE contract_analyses
                        SET contract_version_id = :contract_version_id
                        WHERE id = :analysis_id AND contract_version_id IS NULL
                        """
                    ),
                    {
                        "contract_version_id": chosen_version["id"],
                        "analysis_id": row["id"],
                    },
                )


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
        connect_args={"check_same_thread": False}
        if resolved_database_url.startswith("sqlite")
        else {},
    )
    Base.metadata.create_all(bind=engine)
    _reconcile_legacy_schema(engine)
    app.state.session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    with Session(engine) as session:
        _seed_default_policy(session)

    app.include_router(auth_router)
    app.include_router(policies_router)
    app.include_router(contracts_router)
    app.include_router(uploads_router)
    app.include_router(notifications_router)
    app.include_router(dashboard_router)
    app.include_router(search_router)
    app.state.storage_service = LocalStorageService(resolved_storage_directory)
    app.state.ocr_client = NoopOcrClient()

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

    if openai_api_key:
        app.state.llm_client = OpenAIAnalysisClient(
            api_key=openai_api_key,
            model=openai_model,
        )
        global _embedding_client
        _embedding_client = EmbeddingClient(api_key=openai_api_key)
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
    app.state.jwt_expiration_minutes = int(
        os.environ.get("JWT_EXPIRATION_MINUTES", "480")
    )

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app
