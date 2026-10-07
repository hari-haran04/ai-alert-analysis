from __future__ import annotations

from app.schemas.common import Classification, RiskLevel


class RecommendationService:
    def actions(self, classification: Classification, risk_level: RiskLevel) -> list[str]:
        if classification == Classification.TRUE_ALERT:
            actions = ["Escalate for compliance review", "Verify ownership structure"]
            if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
                actions.insert(0, "Do not close without senior analyst approval")
            return actions
        if classification == Classification.FALSE_POSITIVE:
            return [
                "Document conflicting identity evidence",
                "Review/close according to configured analyst workflow",
            ]
        return [
            "Request additional identifying information",
            "Perform manual analyst review before disposition",
        ]

