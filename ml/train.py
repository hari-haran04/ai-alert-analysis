from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from ml.calibrated_model import ProbabilityCalibratedModel
from ml.feature_engineering import FEATURE_NAMES, vectorize


def load_jsonl(path: str) -> list[dict]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def metrics(y_true, probabilities) -> dict:
    y_pred = [1 if p >= 0.5 else 0 for p in probabilities]
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, probabilities), 4),
        "pr_auc": round(average_precision_score(y_true, probabilities), 4),
        "false_positive_rate": round(fp / (fp + tn), 4) if fp + tn else 0.0,
        "false_negative_rate": round(fn / (fn + tp), 4) if fn + tp else 0.0,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def train(dataset_path: str, output_path: str) -> dict:
    records = load_jsonl(dataset_path)
    x_rows, y_rows = vectorize(records)
    x_train, x_temp, y_train, y_temp = train_test_split(
        x_rows, y_rows, test_size=0.3, random_state=42, stratify=y_rows
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    base_model = XGBClassifier(
        n_estimators=160,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
    )
    base_model.fit(x_train, y_train)
    validation_probabilities = base_model.predict_proba(x_val)[:, 1]
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(validation_probabilities, y_val)
    calibrated = ProbabilityCalibratedModel(base_model, calibrator)
    probabilities = calibrated.predict_proba(x_test)[:, 1]
    model_metrics = metrics(y_test, probabilities)
    metadata = {
        "modelName": "alert-entity-matcher",
        "modelVersion": "1.0.0",
        "trainingDatasetVersion": "synthetic-v1",
        "trainedAt": datetime.now(UTC).isoformat(),
        "features": FEATURE_NAMES,
        "metrics": model_metrics,
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": calibrated, "metadata": metadata}, path)
    metrics_path = Path("ml/metrics/entity_matcher_metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="ml/data/synthetic_pairs.jsonl")
    parser.add_argument("--output", default="ml/models/entity_matcher.joblib")
    args = parser.parse_args()
    print(json.dumps(train(args.dataset, args.output), indent=2))


if __name__ == "__main__":
    main()

