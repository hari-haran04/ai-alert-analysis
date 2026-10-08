from __future__ import annotations

from app.services.case_retrieval import CaseRetrievalService
from scripts.seed_data import seed
from tests.fixtures.samples import FALSE_POSITIVE_ALERT, TRUE_POSITIVE_ALERT


def _similar_cases_for(payload: dict) -> list[dict]:
    seed()
    return CaseRetrievalService().similar_cases_for_third_party(
        payload["thirdParty"], top_k=3
    )


def test_false_positive_alert_retrieves_michael_jordan_case_only():
    cases = _similar_cases_for(FALSE_POSITIVE_ALERT)

    assert cases[0]["caseId"] == "CASE-002"
    assert cases[0]["similarity"] > 0
    assert any("FALSE_POSITIVE" in reason for reason in cases[0]["matchReasons"])
    assert any(match["field"] == "name" for match in cases[0]["fieldMatches"])


def test_true_positive_alert_retrieves_gold_true_alert_case_first():
    cases = _similar_cases_for(TRUE_POSITIVE_ALERT)

    assert cases
    assert cases[0]["caseId"] == "CASE-001"
    assert cases[0]["similarity"] > 0
    assert any("TRUE_ALERT" in reason for reason in cases[0]["matchReasons"])
    assert any(match["field"] == "taxId" for match in cases[0]["fieldMatches"])
