def test_cors_preflight_allows_web_origin(client) -> None:
    response = client.options(
        "/api/uploads/contracts",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
