from __future__ import annotations

from app.schemas.alert import HitIn, ThirdPartyIn
from app.schemas.common import MatchResult
from app.services.attribute_matcher import AttributeMatcher


def test_identifier_match_and_missing_are_distinct():
    matcher = AttributeMatcher()
    assert matcher.compare_tax_id("123", "123").result == MatchResult.MATCH
    assert matcher.compare_tax_id("123", "999").result == MatchResult.MISMATCH
    assert matcher.compare_tax_id("123", None).result == MatchResult.NOT_AVAILABLE


def test_name_handles_punctuation_and_case():
    matcher = AttributeMatcher()
    tp = ThirdPartyIn(name="John-Smith LLC")
    hit = HitIn(hitId="H1", name="JOHN SMITH Limited Liability Company")
    result = matcher.compare_name(tp, hit)
    assert result.result in {MatchResult.MATCH, MatchResult.PARTIAL_MATCH}
    assert result.similarity >= 0.75

