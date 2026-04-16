from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


class EmbeddingClient:
    def __init__(self, api_key: str, model: str = EMBEDDING_MODEL) -> None:
        self._api_key = api_key
        self._model = model
        if openai is None:
            self._client = None
            logger.warning("openai package not installed — embeddings unavailable")
            return
        self._client = openai.OpenAI(api_key=api_key)

    def generate_embedding(self, text: str) -> list[float] | None:
        if not self._client:
            return None
        try:
            response = self._client.embeddings.create(
                model=self._model,
                input=text,
                dimensions=EMBEDDING_DIMENSIONS,
            )
            return response.data[0].embedding
        except Exception:
            logger.exception("Embedding generation failed")
            return None

    def generate_embeddings(self, texts: list[str]) -> list[list[float] | None]:
        if not self._client:
            return [None] * len(texts)
        try:
            response = self._client.embeddings.create(
                model=self._model,
                input=texts,
                dimensions=EMBEDDING_DIMENSIONS,
            )
            return [item.embedding for item in response.data]
        except Exception:
            logger.exception("Batch embedding generation failed")
            return [None] * len(texts)
