from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnalystFeedback(Base):
    __tablename__ = "analyst_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(100), index=True)
    ai_classification: Mapped[str] = mapped_column(String(50))
    analyst_classification: Mapped[str] = mapped_column(String(50))
    analyst_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

