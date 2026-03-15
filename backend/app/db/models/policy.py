from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Policy(TimestampMixin, Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    rules: Mapped[list["PolicyRule"]] = relationship(
        back_populates="policy",
        cascade="all, delete-orphan",
    )


class PolicyRule(TimestampMixin, Base):
    __tablename__ = "policy_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    policy_id: Mapped[str] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict[str, Any] | int | str | float] = mapped_column(JSON, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))

    policy: Mapped[Policy] = relationship(back_populates="rules")
