from __future__ import annotations

from app.schemas.alert import AlertIn
from app.services.attribute_matcher import AttributeMatcher
from app.services.case_retrieval import CaseRetrievalService
from app.services.rule_engine import RuleEngine
from scripts.seed_data import seed
from tests.fixtures.samples import FALSE_POSITIVE_ALERT, TRUE_POSITIVE_ALERT


def _similar_cases_for(payload: dict) -> list[dict]:
    seed()
    alert = AlertIn(**payload)
    attributes = AttributeMatcher(weights=RuleEngine().weights).compare_all(
        alert.third_party, alert.hits[0]
    )
    text = CaseRetrievalService.analysis_text(payload, attributes)
    return CaseRetrievalService().similar_cases(text, top_k=5)


def test_false_positive_alert_retrieves_michael_jordan_case_only():
    cases = _similar_cases_for(FALSE_POSITIVE_ALERT)

    assert [case["caseId"] for case in cases] == ["CASE-002"]
    assert cases[0]["similarity"] > 0
    assert any("FALSE_POSITIVE" in reason for reason in cases[0]["matchReasons"])
    assert any("jordan" in reason for reason in cases[0]["matchReasons"])


def test_true_positive_alert_retrieves_gold_true_alert_case_first():
    cases = _similar_cases_for(TRUE_POSITIVE_ALERT)

    assert cases
    assert cases[0]["caseId"] == "CASE-001"
    assert cases[0]["similarity"] > 0
    assert any("TRUE_ALERT" in reason for reason in cases[0]["matchReasons"])
