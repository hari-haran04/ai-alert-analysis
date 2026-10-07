from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.schemas.alert import HitIn, ThirdPartyIn
from app.services.attribute_matcher import AttributeMatcher
from app.services.rule_engine import RuleEngine
from app.services.scoring_engine import ScoringEngine

FEATURE_NAMES = [
    "name_exact_match",
    "name_fuzzy_similarity",
    "name_embedding_similarity",
    "country_match",
    "city_match",
    "city_similarity",
    "date_of_birth_match",
    "passport_match",
    "tax_id_match",
    "registration_number_match",
    "address_similarity",
    "alias_match",
    "screening_engine_score",
    "screening_level_high",
    "screening_level_medium",
    "list_type_sanctions",
    "source_kharon",
]


def features_for_pair(third_party: dict, hit: dict) -> dict[str, float]:
    rule_engine = RuleEngine()
    matcher = AttributeMatcher(weights=rule_engine.weights)
    scoring = ScoringEngine()
    tp = ThirdPartyIn(**third_party)
    hit_model = HitIn(**hit)
    attributes = matcher.compare_all(tp, hit_model)
    features = scoring.build_features(
        attributes, hit_model.score, hit_model.level, hit_model.list_type, hit_model.source
    )
    return {name: float(features.get(name, 0.0)) for name in FEATURE_NAMES}


def vectorize(records: list[dict]) -> tuple[list[list[float]], list[int]]:
    x_rows: list[list[float]] = []
    y_rows: list[int] = []
    for record in records:
        features = features_for_pair(record["thirdParty"], record["hit"])
        x_rows.append([features[name] for name in FEATURE_NAMES])
        y_rows.append(int(record["label"]))
    return x_rows, y_rows

