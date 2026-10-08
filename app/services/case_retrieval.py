from __future__ import annotations

import json

from app.repositories.memory_store import store
from app.schemas.analysis import AttributeResult
from app.schemas.case import HistoricalCaseIn
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.utils.normalization import normalize_country, normalize_identifier
from app.utils.similarity import ratio, weighted_name_similarity


class CaseRetrievalService:
    minimum_similarity = 0.05
    field_weights = {
        "name": 0.35,
        "country": 0.15,
        "city": 0.10,
        "dateOfBirth": 0.15,
        "passportNumber": 0.15,
        "registrationNumber": 0.15,
        "taxId": 0.10,
        "address": 0.05,
    }

    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or get_embedding_service()

    def add_case(self, case: HistoricalCaseIn) -> dict:
        payload = case.model_dump(by_alias=True)
        payload["embedding"] = self.embedding_service.embed(self._case_text(payload))
        store.save_case(case.case_id, payload)
        return payload

    def get_case(self, case_id: str) -> dict | None:
        return store.get_case(case_id)

    def similar_cases(
        self, alert_text: str, top_k: int = 5, minimum_similarity: float | None = None
    ) -> list[dict]:
        query = self.embedding_service.embed(alert_text)
        cases = []
        threshold = self.minimum_similarity if minimum_similarity is None else minimum_similarity
        for case in store.list_cases():
            embedding = case.get("embedding") or self.embedding_service.embed(self._case_text(case))
            similarity = self.embedding_service.cosine_similarity(query, embedding)
            if similarity < threshold:
                continue
            copy = dict(case)
            copy["similarity"] = round(similarity, 4)
            copy["matchReasons"] = self._match_reasons(alert_text, copy)
            copy.pop("embedding", None)
            cases.append(copy)
        return sorted(cases, key=lambda item: item["similarity"], reverse=True)[:top_k]

    def similar_cases_for_third_party(
        self,
        third_party: dict,
        top_k: int = 3,
        minimum_similarity: float | None = None,
    ) -> list[dict]:
        cases = []
        threshold = self.minimum_similarity if minimum_similarity is None else minimum_similarity
        for case in store.list_cases():
            historical_third_party = (case.get("attributes") or {}).get("thirdParty", {})
            similarity, field_matches = self._third_party_similarity(
                third_party, historical_third_party
            )
            if similarity < threshold:
                continue
            copy = dict(case)
            copy["similarity"] = round(similarity, 4)
            copy["fieldMatches"] = field_matches
            copy["matchReasons"] = [
                f"{item['field']} {item['result'].lower()} ({round(item['similarity'] * 100)}%)"
                for item in field_matches
                if item["result"] in {"MATCH", "PARTIAL_MATCH"}
            ]
            if case.get("classification"):
                copy["matchReasons"].append(f"Prior analyst decision: {case['classification']}")
            copy.pop("embedding", None)
            cases.append(copy)
        return sorted(cases, key=lambda item: item["similarity"], reverse=True)[:top_k]

    @staticmethod
    def alert_text(alert: dict) -> str:
        third_party = alert.get("thirdParty") or alert.get("third_party") or {}
        hit_names = " ".join(hit.get("name", "") for hit in alert.get("hits", []))
        hit_details = " ".join(
            " ".join(str(value) for value in hit.values() if value is not None)
            for hit in alert.get("hits", [])
        )
        return " ".join(
            [
                str(third_party.get("name", "")),
                str(third_party.get("country", "")),
                str(third_party.get("city", "")),
                str(third_party.get("dateOfBirth", "")),
                str(third_party.get("passportNumber", "")),
                str(third_party.get("registrationNumber", "")),
                str(third_party.get("taxId", "")),
                hit_names,
                hit_details,
            ]
        )

    @staticmethod
    def analysis_text(alert: dict, attributes: dict[str, AttributeResult]) -> str:
        evidence = " ".join(
            f"{name} {result.result} {result.evidence}" for name, result in attributes.items()
        )
        return f"{CaseRetrievalService.alert_text(alert)} {evidence}"

    @staticmethod
    def _case_text(case: dict) -> str:
        return " ".join(
            [
                str(case.get("summary", "")),
                str(case.get("classification", "")),
                " ".join(case.get("reasoning", [])),
                json.dumps(case.get("attributes", {}), sort_keys=True, default=str),
            ]
        )

    def _third_party_similarity(
        self, current: dict, historical: dict
    ) -> tuple[float, list[dict]]:
        weighted_score = 0.0
        compared_weight = 0.0
        field_matches: list[dict] = []

        for field, weight in self.field_weights.items():
            current_value = self._field_value(current, field)
            historical_value = self._field_value(historical, field)
            if not current_value or not historical_value:
                continue
            similarity = self._field_similarity(field, current_value, historical_value)
            compared_weight += weight
            weighted_score += similarity * weight
            if similarity >= 0.9:
                result = "MATCH"
            elif similarity >= 0.65:
                result = "PARTIAL_MATCH"
            else:
                result = "MISMATCH"
            field_matches.append(
                {
                    "field": field,
                    "result": result,
                    "similarity": round(similarity, 4),
                }
            )

        if compared_weight == 0:
            return 0.0, []
        return weighted_score / compared_weight, field_matches

    @staticmethod
    def _field_value(payload: dict, field: str) -> str | None:
        if field == "passportNumber":
            return payload.get("passportNumber") or payload.get("passportNumberMasked")
        return payload.get(field)

    @staticmethod
    def _field_similarity(field: str, current_value: str, historical_value: str) -> float:
        if field == "name":
            return weighted_name_similarity(str(current_value), str(historical_value))
        if field in {"city", "address"}:
            return ratio(str(current_value), str(historical_value))
        if field == "country":
            return (
                1.0
                if normalize_country(str(current_value))
                == normalize_country(str(historical_value))
                else 0.0
            )
        if "*" in str(historical_value):
            return CaseRetrievalService._masked_identifier_similarity(
                str(current_value), str(historical_value)
            )
        return (
            1.0
            if normalize_identifier(str(current_value))
            == normalize_identifier(str(historical_value))
            else 0.0
        )

    @staticmethod
    def _masked_identifier_similarity(current_value: str, masked_value: str) -> float:
        current = normalize_identifier(current_value)
        masked = str(masked_value).upper()
        parts = [normalize_identifier(part) for part in masked.split("*") if part]
        if not parts:
            return 0.0
        prefix_ok = current.startswith(parts[0])
        suffix_ok = current.endswith(parts[-1])
        if prefix_ok and suffix_ok:
            return 1.0
        if prefix_ok or suffix_ok:
            return 0.5
        return 0.0

    @staticmethod
    def _match_reasons(alert_text: str, case: dict) -> list[str]:
        alert_tokens = {
            token.lower()
            for token in alert_text.replace("_", " ").replace("-", " ").split()
            if len(token) >= 4
        }
        case_text = CaseRetrievalService._case_text(case).replace("_", " ").replace("-", " ")
        case_tokens = {token.lower() for token in case_text.split() if len(token) >= 4}
        shared = sorted(alert_tokens & case_tokens)
        reasons = [f"Shared signal: {token}" for token in shared[:6]]
        if case.get("classification"):
            reasons.append(f"Prior analyst decision: {case['classification']}")
        return reasons

