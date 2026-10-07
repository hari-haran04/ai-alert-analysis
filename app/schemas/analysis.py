from __future__ import annotations

from pydantic import Field

from app.schemas.common import CamelModel, Classification, MatchResult, RiskLevel


class BestHit(CamelModel):
    hit_id: str = Field(alias="hitId")
    name: str
    screening_score: float | None = Field(default=None, alias="screeningScore")
    screening_level: str | None = Field(default=None, alias="screeningLevel")
    list_type: str | None = Field(default=None, alias="listType")
    source: str | None = None


class RankedHit(CamelModel):
    hit_id: str = Field(alias="hitId")
    rank: int
    match_score: float = Field(alias="matchScore")
    classification: Classification


class AttributeResult(CamelModel):
    result: MatchResult
    similarity: float | None = None
    weight: float = 0.0
    evidence: str


class ModelAnalysis(CamelModel):
    model_version: str = Field(alias="modelVersion")
    prediction: str
    probability: float


class HistoricalEvidence(CamelModel):
    similar_cases_found: int = Field(alias="similarCasesFound")
    cases: list[dict] = Field(default_factory=list)


class AuditInfo(CamelModel):
    rule_version: str = Field(alias="ruleVersion")
    model_version: str = Field(alias="modelVersion")
    input_hash: str = Field(alias="inputHash")
    analyst_review_required: bool = Field(True, alias="analystReviewRequired")


class AnalysisResponse(CamelModel):
    alert_id: str = Field(alias="alertId")
    classification: Classification
    confidence: int = Field(ge=0, le=100)
    risk_level: RiskLevel = Field(alias="riskLevel")
    best_hit: BestHit | None = Field(default=None, alias="bestHit")
    ranked_hits: list[RankedHit] = Field(alias="rankedHits")
    attribute_analysis: dict[str, AttributeResult] = Field(alias="attributeAnalysis")
    model_analysis: ModelAnalysis = Field(alias="modelAnalysis")
    historical_evidence: HistoricalEvidence = Field(alias="historicalEvidence")
    reasoning: list[str]
    recommended_actions: list[str] = Field(alias="recommendedActions")
    audit: AuditInfo
    summary: str | None = None
    compliance_notice: str = Field(
        default=(
            "AI-assisted recommendation only. A human compliance analyst must make "
            "the final decision."
        ),
        alias="complianceNotice",
    )

