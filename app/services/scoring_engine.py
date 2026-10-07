from __future__ import annotations

from app.schemas.common import MatchResult


class ScoringEngine:
    def build_features(
        self, attributes: dict, hit_score: float | None, hit_level: str | None, list_type: str | None, source: str | None
    ) -> dict[str, float]:
        def sim(name: str) -> float:
            value = attributes[name]
            if value.result == MatchResult.MATCH:
                return 1.0
            if value.result == MatchResult.PARTIAL_MATCH:
                return float(value.similarity or 0.0)
            if value.result == MatchResult.MISMATCH:
                return 0.0
            return -1.0

        features = {
            "name_exact_match": 1.0 if attributes["name"].result == MatchResult.MATCH else 0.0,
            "name_fuzzy_similarity": max(0.0, sim("name")),
            "name_embedding_similarity": max(0.0, sim("name")),
            "country_match": 1.0 if attributes["country"].result == MatchResult.MATCH else 0.0,
            "city_match": 1.0 if attributes["city"].result == MatchResult.MATCH else 0.0,
            "city_similarity": max(0.0, sim("city")),
            "date_of_birth_match": 1.0 if attributes["dateOfBirth"].result == MatchResult.MATCH else 0.0,
            "passport_match": 1.0 if attributes["passportNumber"].result == MatchResult.MATCH else 0.0,
            "tax_id_match": 1.0 if attributes["taxId"].result == MatchResult.MATCH else 0.0,
            "registration_number_match": 1.0
            if attributes["registrationNumber"].result == MatchResult.MATCH
            else 0.0,
            "address_similarity": max(0.0, sim("address")),
            "alias_match": 1.0 if attributes["aliases"].result == MatchResult.MATCH else 0.0,
            "screening_engine_score": (hit_score or 0.0) / 100,
            "screening_level_high": 1.0 if (hit_level or "").upper() == "HIGH" else 0.0,
            "screening_level_medium": 1.0 if (hit_level or "").upper() == "MEDIUM" else 0.0,
            "list_type_sanctions": 1.0
            if any(token in (list_type or "").upper() for token in ["SDN", "SANCTIONS", "50PLUS"])
            else 0.0,
            "source_kharon": 1.0 if (source or "").upper() == "KHARON" else 0.0,
        }
        return features

    def confidence(
        self,
        rule_score: float,
        model_probability: float,
        data_quality: float,
        historical_similarity: float,
        has_override: bool,
    ) -> int:
        if has_override:
            return int(round(max(0.88, 1 - rule_score) * 100))
        value = (
            model_probability * 0.35
            + rule_score * 0.4
            + data_quality * 0.15
            + min(historical_similarity, 0.85) * 0.1
        )
        return max(0, min(100, int(round(value * 100))))

