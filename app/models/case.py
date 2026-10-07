from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class HistoricalCase(Base):
    __tablename__ = "historical_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    alert_id: Mapped[str] = mapped_column(String(100), index=True)
    classification: Mapped[str] = mapped_column(String(50), index=True)
    analyst_decision: Mapped[str] = mapped_column(String(50))
    summary: Mapped[str] = mapped_column(Text)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    reasoning: Mapped[list] = mapped_column(JSON, default=list)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

