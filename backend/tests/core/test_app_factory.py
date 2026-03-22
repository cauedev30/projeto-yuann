from app.core.app_factory import _get_database_url, create_app


def test_create_app_wires_runtime_dependencies(monkeypatch, workspace_tmp_path) -> None:
    database_path = workspace_tmp_path / "runtime.db"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
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
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
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


def test_create_app_allows_explicit_cors_origins_from_environment(
    monkeypatch,
    workspace_tmp_path,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
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
