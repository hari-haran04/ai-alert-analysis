from __future__ import annotations

import argparse
import json

import joblib

from ml.feature_engineering import FEATURE_NAMES, vectorize
from ml.train import load_jsonl, metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="ml/data/synthetic_pairs.jsonl")
    parser.add_argument("--model", default="ml/models/entity_matcher.joblib")
    args = parser.parse_args()
    artifact = joblib.load(args.model)
    records = load_jsonl(args.dataset)
    x_rows, y_rows = vectorize(records)
    probabilities = artifact["model"].predict_proba(x_rows)[:, 1]
    output = metrics(y_rows, probabilities)
    output["features"] = FEATURE_NAMES
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

