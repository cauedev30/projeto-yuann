import pytest


@pytest.mark.parametrize("origin", ["http://127.0.0.1:3000", "http://127.0.0.1:3100"])
def test_cors_preflight_allows_web_origin(client, origin: str) -> None:
    response = client.options(
        "/api/uploads/contracts",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
