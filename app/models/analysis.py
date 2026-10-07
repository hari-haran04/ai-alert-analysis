from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


analysis_historical_cases = Table(
    "analysis_historical_cases",
    Base.metadata,
    Column("analysis_id", ForeignKey("analyses.id"), primary_key=True),
    Column("case_id", ForeignKey("historical_cases.id"), primary_key=True),
)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id_fk: Mapped[int | None] = mapped_column(ForeignKey("alerts.id"), nullable=True)
    alert_id: Mapped[str] = mapped_column(String(100), index=True)
    classification: Mapped[str] = mapped_column(String(50), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(50))
    model_version: Mapped[str] = mapped_column(String(50))
    rule_version: Mapped[str] = mapped_column(String(50))
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_hash: Mapped[str] = mapped_column(String(128), index=True)
    model_prediction: Mapped[dict] = mapped_column(JSON, default=dict)
    rule_results: Mapped[dict] = mapped_column(JSON, default=dict)
    historical_cases_used: Mapped[list] = mapped_column(JSON, default=list)
    final_recommendation: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    alert = relationship("Alert", back_populates="analyses")
    attributes: Mapped[list["AttributeAnalysis"]] = relationship(back_populates="analysis")


class AttributeAnalysis(Base):
    __tablename__ = "attribute_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    hit_id: Mapped[str] = mapped_column(String(100), index=True)
    attribute_name: Mapped[str] = mapped_column(String(100))
    result: Mapped[str] = mapped_column(String(50))
    similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight: Mapped[float] = mapped_column(Float)
    evidence: Mapped[str] = mapped_column(String(500))

    analysis: Mapped["Analysis"] = relationship(back_populates="attributes")

