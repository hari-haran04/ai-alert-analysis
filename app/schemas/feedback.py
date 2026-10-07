from __future__ import annotations

from pydantic import Field

from app.schemas.common import CamelModel, Classification


class FeedbackIn(CamelModel):
    alert_id: str = Field(alias="alertId")
    ai_classification: Classification = Field(alias="aiClassification")
    analyst_classification: Classification = Field(alias="analystClassification")
    analyst_comment: str | None = Field(default=None, alias="analystComment")


class FeedbackOut(FeedbackIn):
    feedback_id: str = Field(alias="feedbackId")

