from pathlib import Path

from fastapi.testclient import TestClient

from app.core.app_factory import create_app


def test_create_app_wires_runtime_dependencies() -> None:
    app = create_app(
        database_url="sqlite://",
        storage_directory=Path(__file__).resolve().parent,
    )

    assert callable(app.state.session_factory)
    assert app.state.storage_service is not None
    assert app.state.ocr_client is not None

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
