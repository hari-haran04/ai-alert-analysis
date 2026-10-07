from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.hit import Hit


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    screening_type: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    third_party: Mapped["ThirdParty"] = relationship(back_populates="alert")
    hits: Mapped[list["Hit"]] = relationship(back_populates="alert")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="alert")


class ThirdParty(Base):
    __tablename__ = "third_parties"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[str | None] = mapped_column(String(40), nullable=True)
    passport_number_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    registration_number_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tax_id_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    alert: Mapped["Alert"] = relationship(back_populates="third_party")

