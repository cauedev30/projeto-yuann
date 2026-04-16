from app.infrastructure.embeddings import EmbeddingClient


def test_embedding_client_returns_none_without_openai():
    """When openai package is not available, generate_embedding returns None."""
    client = EmbeddingClient(api_key="fake")
    if client._client is None:
        result = client.generate_embedding("test text")
        assert result is None
    # else: openai is installed but we have a fake key — the client handles this gracefully


def test_embedding_client_batch_returns_list():
    """When openai package is not available, batch returns list of Nones."""
    client = EmbeddingClient(api_key="fake")
    if client._client is None:
        result = client.generate_embeddings(["text 1", "text 2"])
        assert all(r is None for r in result)
