from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


FIRST_NAMES = ["Michael", "John", "Anna", "Sergei", "Mohammed", "Wei", "Maria", "Ivan"]
LAST_NAMES = ["Jordan", "Smith", "Petrov", "Khan", "Chen", "Garcia", "Volkov", "Santos"]
ORG_ROOTS = ["Sakha Gold", "ABC Trading", "Volga Energy", "North River", "Global Metals"]
SUFFIXES = ["Ltd", "Limited", "LLC", "Inc", "Corp", "AO", "JSC", "PLC"]
COUNTRIES = ["USA", "Russia", "UAE", "China", "Brazil", "United Kingdom"]
CITIES = ["Chicago", "New York", "Yakutsk", "Aldan", "Dubai", "Shanghai", "London"]


def typo(value: str) -> str:
    if len(value) < 4:
        return value
    idx = random.randint(1, len(value) - 2)
    return value[:idx] + value[idx + 1] + value[idx] + value[idx + 2 :]


def person() -> dict:
    return {
        "entityId": f"TP{random.randint(10000, 99999)}",
        "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "country": random.choice(COUNTRIES),
        "city": random.choice(CITIES),
        "dateOfBirth": f"{random.randint(1950, 1998)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "passportNumber": f"P{random.randint(10000000, 99999999)}",
        "address": f"{random.randint(1,999)} Main Street",
    }


def organization() -> dict:
    return {
        "entityId": f"TP{random.randint(10000, 99999)}",
        "name": f"{random.choice(ORG_ROOTS)} {random.choice(SUFFIXES)}",
        "country": random.choice(COUNTRIES),
        "city": random.choice(CITIES),
        "registrationNumber": str(random.randint(1000000000, 9999999999)),
        "taxId": str(random.randint(1000000000, 9999999999)),
        "address": f"{random.randint(1,999)} Industrial Road",
    }


def true_hit(tp: dict) -> dict:
    hit = dict(tp)
    hit["hitId"] = f"HIT{random.randint(100000, 999999)}"
    if random.random() < 0.4:
        hit["name"] = typo(hit["name"])
    if " Ltd" in hit["name"] and random.random() < 0.5:
        hit["name"] = hit["name"].replace(" Ltd", " Limited")
    hit["score"] = random.randint(88, 100)
    hit["level"] = random.choice(["HIGH", "MEDIUM"])
    hit["listType"] = random.choice(["US_50PLUS", "OFAC_SDN", "EU_SANCTIONS"])
    hit["source"] = random.choice(["KHARON", "FIRCO", "NETERIUM"])
    return hit


def false_hit(tp: dict) -> dict:
    base = organization() if "registrationNumber" in tp else person()
    hit = dict(base)
    hit["hitId"] = f"HIT{random.randint(100000, 999999)}"
    if random.random() < 0.65:
        hit["name"] = tp["name"] if random.random() < 0.2 else typo(tp["name"])
    if random.random() < 0.55:
        hit["country"] = tp["country"]
    hit["score"] = random.randint(65, 96)
    hit["level"] = random.choice(["LOW", "MEDIUM", "HIGH"])
    hit["listType"] = random.choice(["US_50PLUS", "PEP", "WATCHLIST"])
    hit["source"] = random.choice(["KHARON", "FIRCO", "NETERIUM"])
    return hit


def generate(rows: int, seed: int = 42) -> list[dict]:
    random.seed(seed)
    records = []
    for _ in range(rows):
        tp = organization() if random.random() < 0.5 else person()
        label = 1 if random.random() < 0.5 else 0
        hit = true_hit(tp) if label else false_hit(tp)
        records.append({"thirdParty": tp, "hit": hit, "label": label})
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--output", default="ml/data/synthetic_pairs.jsonl")
    args = parser.parse_args()
    rows = generate(args.rows)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print(f"Wrote {len(rows)} synthetic pairs to {path}")


if __name__ == "__main__":
    main()

