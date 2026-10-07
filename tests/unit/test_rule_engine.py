from __future__ import annotations

from app.schemas.analysis import AttributeResult
from app.schemas.common import Classification, MatchResult
from app.services.rule_engine import RuleEngine


def test_critical_identifier_mismatch_overrides_name_match():
    engine = RuleEngine()
    attributes = {
        "name": AttributeResult(result=MatchResult.MATCH, similarity=1.0, weight=0.2, evidence="Name matched"),
        "country": AttributeResult(result=MatchResult.MATCH, similarity=1.0, weight=0.1, evidence="Country matched"),
        "city": AttributeResult(result=MatchResult.NOT_AVAILABLE, weight=0.05, evidence="City missing"),
        "dateOfBirth": AttributeResult(result=MatchResult.NOT_AVAILABLE, weight=0.2, evidence="DOB missing"),
        "passportNumber": AttributeResult(result=MatchResult.NOT_AVAILABLE, weight=0.2, evidence="Passport missing"),
        "taxId": AttributeResult(result=MatchResult.MISMATCH, similarity=0.0, weight=0.1, evidence="Tax ID mismatch"),
        "registrationNumber": AttributeResult(result=MatchResult.NOT_AVAILABLE, weight=0.15, evidence="Reg missing"),
        "address": AttributeResult(result=MatchResult.NOT_AVAILABLE, weight=0.05, evidence="Address missing"),
        "aliases": AttributeResult(result=MatchResult.NOT_AVAILABLE, weight=0.05, evidence="Alias missing"),
    }
    result = engine.evaluate(attributes)
    assert result["classification"] == Classification.FALSE_POSITIVE
    assert result["override"] == "CRITICAL_IDENTIFIER_MISMATCH"

