from __future__ import annotations

from pathlib import Path

import yaml

from app.core.config import get_settings
from app.schemas.analysis import AttributeResult
from app.schemas.common import Classification, MatchResult


DEFAULT_RULE_CONFIG = {
    "version": "1.0.0",
    "weights": {
        "name": 0.2,
        "country": 0.1,
        "city": 0.05,
        "dateOfBirth": 0.2,
        "passportNumber": 0.2,
        "registrationNumber": 0.15,
        "taxId": 0.1,
        "address": 0.05,
        "alias": 0.05,
    },
    "thresholds": {
        "trueAlert": 0.85,
        "falsePositive": 0.3,
        "inconclusiveLow": 0.45,
        "inconclusiveHigh": 0.75,
    },
    "priorities": {
        "taxId": "CRITICAL",
        "registrationNumber": "CRITICAL",
        "passportNumber": "HIGH",
        "dateOfBirth": "HIGH",
        "name": "MEDIUM",
        "country": "MEDIUM",
        "city": "LOW",
    },
    "risk": {
        "criticalListTypes": ["OFAC_SDN", "UN_SANCTIONS"],
        "highListTypes": ["US_50PLUS", "EU_SANCTIONS", "UK_SANCTIONS"],
    },
}


class RuleEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.config = self._load_rules()

    @property
    def version(self) -> str:
        return str(self.config.get("version", self.settings.rule_version))

    @property
    def weights(self) -> dict[str, float]:
        return dict(self.config.get("weights", DEFAULT_RULE_CONFIG["weights"]))

    def update_config(self, config: dict) -> dict:
        self.config = config
        path = self.settings.resolve_project_path(self.settings.rule_config_path)
        path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        return self.config

    def evaluate(self, attributes: dict[str, AttributeResult]) -> dict:
        weighted_score = 0.0
        available_weight = 0.0
        positive_signals: list[str] = []
        negative_signals: list[str] = []
        critical_mismatches: list[str] = []
        high_mismatches: list[str] = []
        missing_attributes: list[str] = []

        priorities = self.config.get("priorities", {})
        for attribute, result in attributes.items():
            weight = result.weight
            if result.result == MatchResult.NOT_AVAILABLE:
                missing_attributes.append(attribute)
                continue
            available_weight += weight
            if result.result == MatchResult.MATCH:
                weighted_score += weight
                positive_signals.append(attribute)
            elif result.result == MatchResult.PARTIAL_MATCH:
                weighted_score += weight * (result.similarity or 0.5)
                positive_signals.append(attribute)
            elif result.result == MatchResult.MISMATCH:
                priority = priorities.get(attribute, "LOW")
                negative_signals.append(attribute)
                if priority == "CRITICAL":
                    critical_mismatches.append(attribute)
                elif priority == "HIGH":
                    high_mismatches.append(attribute)

        normalized_score = weighted_score / available_weight if available_weight else 0.0
        thresholds = self.config.get("thresholds", {})
        true_threshold = thresholds.get("trueAlert", 0.85)
        false_threshold = thresholds.get("falsePositive", 0.3)

        override = None
        if critical_mismatches:
            override = "CRITICAL_IDENTIFIER_MISMATCH"
            classification = Classification.FALSE_POSITIVE
        elif len(high_mismatches) >= 2:
            override = "MULTIPLE_HIGH_IDENTIFIER_MISMATCHES"
            classification = Classification.FALSE_POSITIVE
        elif normalized_score >= true_threshold and not high_mismatches:
            classification = Classification.TRUE_ALERT
        elif normalized_score <= false_threshold:
            classification = Classification.FALSE_POSITIVE
        else:
            classification = Classification.INCONCLUSIVE

        return {
            "classification": classification,
            "ruleScore": round(normalized_score, 4),
            "positiveSignals": positive_signals,
            "negativeSignals": negative_signals,
            "criticalMismatches": critical_mismatches,
            "highMismatches": high_mismatches,
            "missingAttributes": missing_attributes,
            "override": override,
            "version": self.version,
        }

    def _load_rules(self) -> dict:
        path = self.settings.resolve_project_path(self.settings.rule_config_path)
        if Path(path).exists():
            return yaml.safe_load(path.read_text(encoding="utf-8")) or DEFAULT_RULE_CONFIG
        return DEFAULT_RULE_CONFIG

