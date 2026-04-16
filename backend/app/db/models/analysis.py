from __future__ import annotations

import enum
from typing import Any
from uuid import uuid4

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB as JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class ContractAnalysis(TimestampMixin, Base):
    __tablename__ = "contract_analyses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    contract_id: Mapped[str | None] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE")
    )
    contract_version_id: Mapped[str] = mapped_column(
        ForeignKey("contract_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    policy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, name="analysis_status"),
        nullable=False,
        default=AnalysisStatus.pending,
    )
    contract_risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # New fields for corrected contract storage
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrections_summary: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    contract: Mapped["Contract"] = relationship(back_populates="analyses")
    contract_version: Mapped["ContractVersion"] = relationship(
        back_populates="analyses"
    )
    findings: Mapped[list["ContractAnalysisFinding"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class ContractAnalysisFinding(TimestampMixin, Base):
    __tablename__ = "contract_analysis_findings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    analysis_id: Mapped[str] = mapped_column(
        ForeignKey("contract_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    clause_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    current_summary: Mapped[str] = mapped_column(Text, nullable=False)
    policy_rule: Mapped[str] = mapped_column(Text, nullable=False)
    risk_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_adjustment_direction: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    analysis: Mapped[ContractAnalysis] = relationship(back_populates="findings")
