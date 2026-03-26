from collections.abc import Generator
import socket
import threading
import time

import pytest
import httpx
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import create_session_factory
from app.main import app
from app.services.storage import LocalStorageService


class ApiTestClient:
    def __init__(self, *, app, base_url: str) -> None:
        self.app = app
        self._client = httpx.Client(base_url=base_url, timeout=10.0)

    def get(self, *args, **kwargs):
        return self._client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._client.post(*args, **kwargs)

    def options(self, *args, **kwargs):
        return self._client.options(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._client.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._client.delete(*args, **kwargs)

    def close(self) -> None:
        self._client.close()


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture()
def client(workspace_tmp_path) -> Generator[ApiTestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    app.state.session_factory = create_session_factory(engine)
    app.state.storage_service = LocalStorageService(workspace_tmp_path / "uploads")
    port = _find_free_port()
    server = uvicorn.Server(
        uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=port,
            log_level="error",
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)
    if not server.started:
        server.should_exit = True
        thread.join(timeout=5)
        raise RuntimeError("Uvicorn test server did not start")

    test_client = ApiTestClient(app=app, base_url=f"http://127.0.0.1:{port}")
    try:
        yield test_client
    finally:
        test_client.close()
        server.should_exit = True
        thread.join(timeout=5)
