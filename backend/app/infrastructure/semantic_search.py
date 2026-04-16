from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.embeddings import EmbeddingClient


@dataclass
class SearchResult:
    contract_id: str
    contract_title: str
    chunk_type: str
    chunk_text: str
    similarity_score: float


def search_similar_contracts(
    *,
    session: Session,
    query_embedding: list[float],
    limit: int = 10,
    min_similarity: float = 0.5,
) -> list[SearchResult]:
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    results = session.execute(
        text("""
            SELECT
                ce.contract_id,
                c.title AS contract_title,
                ce.chunk_type,
                ce.chunk_text,
                1 - (ce.embedding <=> :query_embedding::vector) AS similarity
            FROM contract_embeddings ce
            JOIN contracts c ON c.id = ce.contract_id
            WHERE 1 - (ce.embedding <=> :query_embedding::vector) > :min_similarity
            ORDER BY ce.embedding <=> :query_embedding::vector
            LIMIT :limit
        """),
        {
            "query_embedding": embedding_str,
            "min_similarity": min_similarity,
            "limit": limit,
        },
    ).fetchall()

    return [
        SearchResult(
            contract_id=row.contract_id,
            contract_title=row.contract_title,
            chunk_type=row.chunk_type,
            chunk_text=row.chunk_text,
            similarity_score=float(row.similarity),
        )
        for row in results
    ]
