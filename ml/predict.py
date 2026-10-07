from __future__ import annotations

import argparse
import json

from app.services.ml_service import MLModelService
from ml.feature_engineering import features_for_pair


def predict(third_party: dict, hit: dict) -> dict:
    features = features_for_pair(third_party, hit)
    service = MLModelService()
    probability = service.predict_probability(features)
    return {
        "prediction": "TRUE_POSITIVE" if probability >= 0.5 else "FALSE_POSITIVE",
        "probability": probability,
        "modelVersion": service.metadata.get("modelVersion", "1.0.0"),
        "features": features,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--third-party-json", required=True)
    parser.add_argument("--hit-json", required=True)
    args = parser.parse_args()
    print(json.dumps(predict(json.loads(args.third_party_json), json.loads(args.hit_json)), indent=2))


if __name__ == "__main__":
    main()

