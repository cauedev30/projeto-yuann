def test_create_policy_returns_201(client) -> None:
    payload = {
        "name": "Padrao Franquia",
        "version": "2026.03",
        "rules": [
            {"code": "MIN_TERM_MONTHS", "value": 60},
            {"code": "MAX_FINE_MONTHS", "value": 3},
        ],
    }

    response = client.post("/api/policies", json=payload)

    assert response.status_code == 201
    assert response.json()["version"] == "2026.03"
