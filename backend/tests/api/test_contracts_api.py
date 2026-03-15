def test_list_contracts_returns_empty_collection(client) -> None:
    response = client.get("/api/contracts")

    assert response.status_code == 200
    assert response.json() == {"items": []}
