from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import create_session_factory
from app.main import app
from app.services.storage import LocalStorageService


@pytest.fixture()
def client(workspace_tmp_path) -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    app.state.session_factory = create_session_factory(engine)
    app.state.storage_service = LocalStorageService(workspace_tmp_path / "uploads")

    with TestClient(app) as test_client:
        yield test_client
