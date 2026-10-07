from __future__ import annotations

from ml.generate_dataset import generate
from ml.train import train

if __name__ == "__main__":
    dataset = "ml/data/synthetic_pairs.jsonl"
    import json
    from pathlib import Path

    path = Path(dataset)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = generate(10000)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print(train(dataset, "ml/models/entity_matcher.joblib"))

