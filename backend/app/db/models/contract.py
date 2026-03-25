from __future__ import annotations

import enum
from typing import Any
from uuid import uuid4

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ContractSource(str, enum.Enum):
    third_party_draft = "third_party_draft"
    signed_contract = "signed_contract"


class Contract(TimestampMixin, Base):
    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    external_reference: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    signature_date: Mapped[date | None] = mapped_column(Date)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    term_months: Mapped[int | None] = mapped_column(Integer)
    parties: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    financial_terms: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    versions: Mapped[list["ContractVersion"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )
    analyses: Mapped[list["ContractAnalysis"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["ContractEvent"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )


class ContractVersion(TimestampMixin, Base):
    __tablename__ = "contract_versions"
    __table_args__ = (UniqueConstraint("contract_id", "version_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[ContractSource] = mapped_column(
        Enum(ContractSource, name="contract_source"),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    text_content: Mapped[str | None] = mapped_column(Text)
    extraction_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    contract: Mapped[Contract] = relationship(back_populates="versions")
    analyses: Mapped[list["ContractAnalysis"]] = relationship(back_populates="contract_version")
