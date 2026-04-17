from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.infrastructure.embeddings import EmbeddingClient
from app.infrastructure.semantic_search import SearchResult, search_similar_contracts

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    min_similarity: float = 0.5


class SearchResponseItem(BaseModel):
    contract_id: str
    contract_title: str
    chunk_type: str
    chunk_text: str
    similarity_score: float


class SearchResponse(BaseModel):
    results: list[SearchResponseItem]


@router.post("", response_model=SearchResponse)
def search_contracts(
    payload: SearchRequest,
    session: Session = Depends(get_session),
) -> SearchResponse:
    from app.core.app_factory import get_embedding_client

    embedding_client = get_embedding_client()
    if embedding_client is None:
        raise HTTPException(status_code=503, detail="Embedding service not configured")

    query_embedding = embedding_client.generate_embedding(payload.query)
    if query_embedding is None:
        raise HTTPException(
            status_code=503, detail="Failed to generate query embedding"
        )

    try:
        results = search_similar_contracts(
            session=session,
            query_embedding=query_embedding,
            limit=payload.limit,
            min_similarity=payload.min_similarity,
        )
    except (OperationalError, Exception) as exc:
        err_msg = str(exc).lower()
        if "vector" in err_msg or "pgvector" in err_msg or "embedding" in err_msg:
            raise HTTPException(
                status_code=503,
                detail="Semantic search unavailable. pgvector extension not enabled on this database.",
            )
        raise HTTPException(
            status_code=503,
            detail=f"Search service error: {str(exc)[:200]}",
        )

    return SearchResponse(
        results=[
            SearchResponseItem(
                contract_id=r.contract_id,
                contract_title=r.contract_title,
                chunk_type=r.chunk_type,
                chunk_text=r.chunk_text,
                similarity_score=r.similarity_score,
            )
            for r in results
        ]
    )
