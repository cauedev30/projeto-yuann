from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import create_session_factory


@pytest.fixture()
def workspace_tmp_path() -> Generator[Path, None, None]:
    base_dir = Path(__file__).resolve().parents[2] / "tmp" / "backend-tests"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = base_dir / str(uuid4())
    temp_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = create_session_factory(engine)
    db_session = session_factory()
    try:
        yield db_session
    finally:
        db_session.close()
