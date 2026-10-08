from __future__ import annotations

import json

from app.repositories.memory_store import store
from app.schemas.analysis import AttributeResult
from app.schemas.case import HistoricalCaseIn
from app.services.embedding_service import EmbeddingService, get_embedding_service


class CaseRetrievalService:
    minimum_similarity = 0.24

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

