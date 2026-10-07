from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Hit(Base):
    __tablename__ = "hits"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), index=True)
    hit_id: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[str | None] = mapped_column(String(40), nullable=True)
    passport_number_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    registration_number_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tax_id_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    list_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    alert = relationship("Alert", back_populates="hits")

