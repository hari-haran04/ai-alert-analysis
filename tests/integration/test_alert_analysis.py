from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from scripts.seed_data import seed
from tests.fixtures.samples import FALSE_POSITIVE_ALERT, TRUE_POSITIVE_ALERT


client = TestClient(app)
seed()


def test_true_positive_example():
    response = client.post("/api/v1/alerts/analyze", json=TRUE_POSITIVE_ALERT)
    assert response.status_code == 200
    body = response.json()
    assert body["classification"] == "TRUE_ALERT"
    assert body["bestHit"]["hitId"] == "HIT001"
    assert body["confidence"] >= 80
    assert body["attributeAnalysis"]["registrationNumber"]["result"] == "MATCH"
    assert body["attributeAnalysis"]["taxId"]["result"] == "MATCH"


def test_false_positive_example():
    response = client.post("/api/v1/alerts/analyze", json=FALSE_POSITIVE_ALERT)
    assert response.status_code == 200
    body = response.json()
    assert body["classification"] == "FALSE_POSITIVE"
    assert body["attributeAnalysis"]["dateOfBirth"]["result"] == "MISMATCH"
    assert body["attributeAnalysis"]["passportNumber"]["result"] == "MISMATCH"
    cases = body["historicalEvidence"]["cases"]
    assert cases
    assert cases[0]["caseId"] == "CASE-002"
    assert cases[0]["similarity"] > 0
    assert any("FALSE_POSITIVE" in reason for reason in cases[0]["matchReasons"])


def test_true_positive_retrieves_relevant_historical_case():
    response = client.post("/api/v1/alerts/analyze", json=TRUE_POSITIVE_ALERT)
    assert response.status_code == 200
    body = response.json()
    cases = body["historicalEvidence"]["cases"]
    assert cases
    assert cases[0]["caseId"] == "CASE-001"
    assert cases[0]["similarity"] > 0


def test_invalid_empty_hits():
    payload = dict(TRUE_POSITIVE_ALERT)
    payload["hits"] = []
    response = client.post("/api/v1/alerts/analyze", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_ALERT"

