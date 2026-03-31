import sqlite3

from app.api.routes.contracts import list_contracts
from app.application.dashboard import build_dashboard_snapshot
from app.core.app_factory import _get_database_url, create_app


def test_create_app_wires_runtime_dependencies(monkeypatch, workspace_tmp_path) -> None:
    database_path = workspace_tmp_path / "runtime.db"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    app = create_app(
        database_url=f"sqlite:///{database_path}",
        storage_directory=workspace_tmp_path / "uploads",
    )

    assert callable(app.state.session_factory)
    assert app.state.storage_service is not None
    assert app.state.ocr_client is not None
    assert any(getattr(route, "path", None) == "/health" for route in app.routes)


def test_create_app_reads_database_url_and_upload_dir_from_environment(
    monkeypatch,
    workspace_tmp_path,
) -> None:
    database_path = workspace_tmp_path / "production.db"
    upload_path = workspace_tmp_path / "production-uploads"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("UPLOAD_DIR", str(upload_path))

    app = create_app()

    engine = app.state.session_factory.kw["bind"]
    assert engine.url.database == str(database_path)
    assert app.state.storage_service.root == upload_path


def test_database_url_is_normalized_for_railway_postgres_urls() -> None:
    assert _get_database_url("postgresql://user:pass@db.example.com/legalboard").startswith(
        "postgresql+psycopg://"
    )
    assert _get_database_url("postgres://user:pass@db.example.com/legalboard").startswith(
        "postgresql+psycopg://"
    )


def test_database_url_defaults_to_clean_local_sqlite_runtime() -> None:
    assert _get_database_url(None) == "sqlite:///./legaltech.db"


def test_create_app_allows_explicit_cors_origins_from_environment(
    monkeypatch,
    workspace_tmp_path,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://yuann.vercel.app, https://app.example.com",
    )
    app = create_app(database_url=f"sqlite:///{workspace_tmp_path / 'cors.db'}")
    cors_middleware = next(
        middleware
        for middleware in app.user_middleware
        if middleware.cls.__name__ == "CORSMiddleware"
    )

    assert cors_middleware.kwargs["allow_origins"] == [
        "https://yuann.vercel.app",
        "https://app.example.com",
    ]


def test_create_app_wires_openai_client_with_default_model(monkeypatch, workspace_tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    app = create_app(database_url=f"sqlite:///{workspace_tmp_path / 'openai-default.db'}")

    assert app.state.llm_client is not None
    assert app.state.llm_client.__class__.__name__ == "OpenAIAnalysisClient"
    assert app.state.llm_client._model == "gpt-5-mini"


def test_create_app_allows_openai_model_override(monkeypatch, workspace_tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.4-mini")

    app = create_app(database_url=f"sqlite:///{workspace_tmp_path / 'openai-override.db'}")

    assert app.state.llm_client is not None
    assert app.state.llm_client._model == "gpt-5.4-mini"


def test_create_app_reconciles_legacy_schema_for_dashboard_and_contracts(
    monkeypatch,
    workspace_tmp_path,
) -> None:
    database_path = workspace_tmp_path / "legacy.db"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE policies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE policy_rules (
                id TEXT PRIMARY KEY,
                policy_id TEXT NOT NULL,
                code TEXT NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE contracts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                external_reference TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                parties TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE contract_versions (
                id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                source TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                storage_key TEXT NOT NULL,
                text_content TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE contract_analyses (
                id TEXT PRIMARY KEY,
                contract_id TEXT,
                policy_version TEXT NOT NULL,
                status TEXT NOT NULL,
                contract_risk_score NUMERIC,
                raw_payload TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE contract_events (
                id TEXT PRIMARY KEY,
                contract_id TEXT,
                event_type TEXT NOT NULL,
                event_date TEXT,
                lead_time_days INTEGER NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE notifications (
                id TEXT PRIMARY KEY,
                contract_event_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                recipient TEXT NOT NULL,
                status TEXT NOT NULL,
                idempotency_key TEXT NOT NULL UNIQUE,
                sent_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    app = create_app(database_url=f"sqlite:///{database_path}")
    with app.state.session_factory() as session:
        dashboard_snapshot = build_dashboard_snapshot(session=session, today="2026-04-01")
        contracts_response = list_contracts(page=1, per_page=20, scope="all", session=session)

    assert dashboard_snapshot.summary.active_contracts == 0
    assert contracts_response.total == 0

    with sqlite3.connect(database_path) as connection:
        contracts_columns = {
            row[1] for row in connection.execute("PRAGMA table_info('contracts')").fetchall()
        }
        contract_version_columns = {
            row[1] for row in connection.execute("PRAGMA table_info('contract_versions')").fetchall()
        }
        contract_analysis_columns = {
            row[1] for row in connection.execute("PRAGMA table_info('contract_analyses')").fetchall()
        }

    assert {"signature_date", "financial_terms", "is_active", "last_analyzed_at"} <= contracts_columns
    assert {"extraction_metadata", "version_number"} <= contract_version_columns
    assert {"contract_version_id", "corrected_text", "corrections_summary"} <= contract_analysis_columns
