from __future__ import annotations

from app.schemas.common import RiskLevel


class RiskEngine:
    def calculate(self, hit: dict, rule_config: dict) -> RiskLevel:
        list_type = (hit.get("listType") or "").upper()
        level = (hit.get("screeningLevel") or "").upper()
        match_score = hit.get("matchScore", 0.0)
        critical_list_types = set(rule_config.get("risk", {}).get("criticalListTypes", []))
        high_list_types = set(rule_config.get("risk", {}).get("highListTypes", []))

        if hit.get("criticalMismatches"):
            return RiskLevel.LOW if match_score < 0.35 else RiskLevel.MEDIUM
        if any(item in list_type for item in critical_list_types) and match_score >= 0.8:
            return RiskLevel.CRITICAL
        if level == "HIGH" and (match_score >= 0.75 or list_type in high_list_types):
            return RiskLevel.HIGH
        if match_score >= 0.85:
            return RiskLevel.HIGH
        if match_score >= 0.5:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

