from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class EventType(str, enum.Enum):
    renewal = "renewal"
    expiration = "expiration"
    readjustment = "readjustment"
    grace_period_end = "grace_period_end"


class NotificationChannel(str, enum.Enum):
    email = "email"
    in_app = "in_app"


class ContractEvent(TimestampMixin, Base):
    __tablename__ = "contract_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    contract_id: Mapped[str | None] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"))
    event_type: Mapped[EventType | str] = mapped_column(
        Enum(EventType, name="event_type"),
        nullable=False,
    )
    event_date: Mapped[date | None] = mapped_column(Date)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    contract: Mapped["Contract"] = relationship(back_populates="events")
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    contract_event_id: Mapped[str] = mapped_column(
        ForeignKey("contract_events.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, name="notification_channel"),
        nullable=False,
    )
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    event: Mapped["ContractEvent"] = relationship(back_populates="notifications")
