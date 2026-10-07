from __future__ import annotations

from app.schemas.alert import HitIn, ThirdPartyIn
from app.schemas.analysis import AttributeResult
from app.schemas.common import MatchResult
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.utils.normalization import (
    normalize_country,
    normalize_date,
    normalize_identifier,
    normalize_text,
)
from app.utils.similarity import ratio, weighted_name_similarity


class AttributeMatcher:
    def __init__(
        self,
        weights: dict[str, float] | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.weights = weights or {}
        self.embedding_service = embedding_service or get_embedding_service()

    def compare_all(self, third_party: ThirdPartyIn, hit: HitIn) -> dict[str, AttributeResult]:
        return {
            "name": self.compare_name(third_party, hit),
            "country": self.compare_country(third_party.country, hit.country),
            "city": self.compare_city(third_party.city, hit.city),
            "dateOfBirth": self.compare_date_of_birth(
                third_party.date_of_birth, hit.date_of_birth
            ),
            "passportNumber": self.compare_passport(
                third_party.passport_number or third_party.passport,
                hit.passport_number or hit.passport,
            ),
            "taxId": self.compare_tax_id(third_party.tax_id, hit.tax_id),
            "registrationNumber": self.compare_registration_number(
                third_party.registration_number, hit.registration_number
            ),
            "address": self.compare_address(third_party.address, hit.address),
            "aliases": self.compare_aliases(third_party.aliases, [hit.name, *hit.aliases]),
        }

    def compare_name(self, third_party: ThirdPartyIn, hit: HitIn) -> AttributeResult:
        left_text = " ".join([third_party.name, *third_party.aliases])
        right_text = " ".join([hit.name, *hit.aliases])
        embedding_similarity = self.embedding_service.cosine_similarity(
            self.embedding_service.embed(left_text), self.embedding_service.embed(right_text)
        )
        similarity = weighted_name_similarity(
            third_party.name, hit.name, embedding_similarity=embedding_similarity
        )
        if similarity >= 0.93:
            result = MatchResult.MATCH
            evidence = f"Name matched {round(similarity * 100)}%"
        elif similarity >= 0.72:
            result = MatchResult.PARTIAL_MATCH
            evidence = f"Name partially matched {round(similarity * 100)}%"
        else:
            result = MatchResult.MISMATCH
            evidence = f"Name similarity was {round(similarity * 100)}%"
        return AttributeResult(
            result=result,
            similarity=similarity,
            weight=self.weights.get("name", 0.2),
            evidence=evidence,
        )

    def compare_country(self, left: str | None, right: str | None) -> AttributeResult:
        return self._compare_exact_text("country", left, right, self.weights.get("country", 0.1))

    def compare_city(self, left: str | None, right: str | None) -> AttributeResult:
        if not left or not right:
            return self._not_available("city", self.weights.get("city", 0.05))
        similarity = ratio(left, right)
        if normalize_text(left) == normalize_text(right):
            return AttributeResult(
                result=MatchResult.MATCH,
                similarity=1.0,
                weight=self.weights.get("city", 0.05),
                evidence="City matched",
            )
        if similarity >= 0.82:
            return AttributeResult(
                result=MatchResult.PARTIAL_MATCH,
                similarity=similarity,
                weight=self.weights.get("city", 0.05),
                evidence=f"City partially matched {round(similarity * 100)}%",
            )
        return AttributeResult(
            result=MatchResult.MISMATCH,
            similarity=similarity,
            weight=self.weights.get("city", 0.05),
            evidence="City mismatch",
        )

    def compare_date_of_birth(self, left, right) -> AttributeResult:
        return self._compare_identifier(
            "date of birth",
            normalize_date(left),
            normalize_date(right),
            self.weights.get("dateOfBirth", 0.2),
        )

    def compare_passport(self, left: str | None, right: str | None) -> AttributeResult:
        return self._compare_identifier(
            "passport", left, right, self.weights.get("passportNumber", 0.2)
        )

    def compare_tax_id(self, left: str | None, right: str | None) -> AttributeResult:
        return self._compare_identifier("tax ID", left, right, self.weights.get("taxId", 0.1))

    def compare_registration_number(
        self, left: str | None, right: str | None
    ) -> AttributeResult:
        return self._compare_identifier(
            "registration number",
            left,
            right,
            self.weights.get("registrationNumber", 0.15),
        )

    def compare_address(self, left: str | None, right: str | None) -> AttributeResult:
        if not left or not right:
            return self._not_available("address", self.weights.get("address", 0.05))
        similarity = ratio(left, right)
        if similarity >= 0.9:
            result = MatchResult.MATCH
            evidence = f"Address matched {round(similarity * 100)}%"
        elif similarity >= 0.72:
            result = MatchResult.PARTIAL_MATCH
            evidence = f"Address partially matched {round(similarity * 100)}%"
        else:
            result = MatchResult.MISMATCH
            evidence = f"Address similarity was {round(similarity * 100)}%"
        return AttributeResult(
            result=result,
            similarity=similarity,
            weight=self.weights.get("address", 0.05),
            evidence=evidence,
        )

    def compare_aliases(self, left: list[str], right: list[str]) -> AttributeResult:
        if not left or not right:
            return self._not_available("aliases", self.weights.get("alias", 0.05))
        best = max((weighted_name_similarity(a, b) for a in left for b in right), default=0.0)
        if best >= 0.9:
            result = MatchResult.MATCH
            evidence = f"Alias matched {round(best * 100)}%"
        elif best >= 0.72:
            result = MatchResult.PARTIAL_MATCH
            evidence = f"Alias partially matched {round(best * 100)}%"
        else:
            result = MatchResult.MISMATCH
            evidence = "No alias match"
        return AttributeResult(
            result=result,
            similarity=best,
            weight=self.weights.get("alias", 0.05),
            evidence=evidence,
        )

    def _compare_exact_text(
        self, label: str, left: str | None, right: str | None, weight: float
    ) -> AttributeResult:
        if not left or not right:
            return self._not_available(label, weight)
        if normalize_country(left) == normalize_country(right):
            return AttributeResult(
                result=MatchResult.MATCH,
                similarity=1.0,
                weight=weight,
                evidence=f"{label.title()} matched",
            )
        return AttributeResult(
            result=MatchResult.MISMATCH,
            similarity=0.0,
            weight=weight,
            evidence=f"{label.title()} mismatch",
        )

    def _compare_identifier(
        self, label: str, left: str | None, right: str | None, weight: float
    ) -> AttributeResult:
        if not left or not right:
            return self._not_available(label, weight)
        normalized_left = normalize_identifier(str(left))
        normalized_right = normalize_identifier(str(right))
        if normalized_left == normalized_right:
            return AttributeResult(
                result=MatchResult.MATCH,
                similarity=1.0,
                weight=weight,
                evidence=f"{label.title()} matched",
            )
        return AttributeResult(
            result=MatchResult.MISMATCH,
            similarity=0.0,
            weight=weight,
            evidence=f"{label.title()} mismatch",
        )

    @staticmethod
    def _not_available(label: str, weight: float) -> AttributeResult:
        return AttributeResult(
            result=MatchResult.NOT_AVAILABLE,
            similarity=None,
            weight=weight,
            evidence=f"{label.title()} not available",
        )

