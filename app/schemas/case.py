from __future__ import annotations

from pydantic import Field

from app.schemas.common import CamelModel, Classification


class HistoricalCaseIn(CamelModel):
    case_id: str = Field(..., alias="caseId")
    alert_id: str = Field(..., alias="alertId")
    classification: Classification
    attributes: dict = Field(default_factory=dict)
    reasoning: list[str] = Field(default_factory=list)
    analyst_decision: Classification = Field(alias="analystDecision")
    summary: str


class HistoricalCaseOut(HistoricalCaseIn):
    similarity: float | None = None

