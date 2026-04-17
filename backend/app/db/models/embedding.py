from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB as PgJSONB
from sqlalchemy.dialects.sqlite import JSON as SqJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None  # type: ignore

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.contract import Contract


class ContractEmbedding(TimestampMixin, Base):
    __tablename__ = "contract_embeddings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    contract_id: Mapped[str] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False
    )
    chunk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    if Vector is not None:
        embedding = mapped_column(Vector(1536), nullable=False)
    else:
        embedding = mapped_column(Text, nullable=False)

    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        SqJSON().with_variant(PgJSONB, "postgresql")
    )

    contract: Mapped["Contract"] = relationship(back_populates="embeddings")
