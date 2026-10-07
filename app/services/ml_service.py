from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import joblib

from app.core.config import get_settings


class MLModelService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = None
        self.metadata = {
            "modelName": "alert-entity-matcher",
            "modelVersion": "1.0.0",
            "trainingDatasetVersion": "synthetic-v1",
            "trainedAt": None,
            "features": [],
            "metrics": {},
        }
        self._load()

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def predict_probability(self, features: dict[str, float]) -> float:
        if self.model is not None:
            ordered = self.metadata.get("features") or list(features.keys())
            row = [[features.get(name, 0.0) for name in ordered]]
            return float(self.model.predict_proba(row)[0][1])
        return self._heuristic_probability(features)

    def _load(self) -> None:
        path = self.settings.resolve_project_path(self.settings.model_path)
        if not Path(path).exists():
            return
        artifact = joblib.load(path)
        self.model = artifact.get("model")
        self.metadata = artifact.get("metadata", self.metadata)

    @staticmethod
    def _heuristic_probability(features: dict[str, float]) -> float:
        critical_identity = max(
            features.get("tax_id_match", 0.0),
            features.get("registration_number_match", 0.0),
            features.get("passport_match", 0.0),
            features.get("date_of_birth_match", 0.0),
        )
        score = (
            features.get("name_fuzzy_similarity", 0.0) * 0.25
            + features.get("country_match", 0.0) * 0.1
            + features.get("city_similarity", 0.0) * 0.05
            + critical_identity * 0.35
            + features.get("screening_engine_score", 0.0) * 0.15
            + features.get("list_type_sanctions", 0.0) * 0.1
        )
        return max(0.02, min(0.98, score))

    def metadata_response(self) -> dict:
        payload = dict(self.metadata)
        payload.setdefault("trainedAt", datetime.now(UTC).isoformat())
        payload["loaded"] = self.loaded
        return payload

