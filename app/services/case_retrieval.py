from __future__ import annotations

from app.repositories.memory_store import store
from app.schemas.case import HistoricalCaseIn
from app.services.embedding_service import EmbeddingService, get_embedding_service


class CaseRetrievalService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or get_embedding_service()

    def add_case(self, case: HistoricalCaseIn) -> dict:
        payload = case.model_dump(by_alias=True)
        payload["embedding"] = self.embedding_service.embed(self._case_text(payload))
        store.save_case(case.case_id, payload)
        return payload

    def get_case(self, case_id: str) -> dict | None:
        return store.get_case(case_id)

    def similar_cases(self, alert_text: str, top_k: int = 5) -> list[dict]:
        query = self.embedding_service.embed(alert_text)
        cases = []
        for case in store.list_cases():
            embedding = case.get("embedding") or self.embedding_service.embed(self._case_text(case))
            similarity = self.embedding_service.cosine_similarity(query, embedding)
            copy = dict(case)
            copy["similarity"] = round(similarity, 4)
            copy.pop("embedding", None)
            cases.append(copy)
        return sorted(cases, key=lambda item: item["similarity"], reverse=True)[:top_k]

    @staticmethod
    def alert_text(alert: dict) -> str:
        third_party = alert.get("thirdParty") or alert.get("third_party") or {}
        hit_names = " ".join(hit.get("name", "") for hit in alert.get("hits", []))
        return " ".join(
            [
                str(third_party.get("name", "")),
                str(third_party.get("country", "")),
                str(third_party.get("city", "")),
                hit_names,
            ]
        )

    @staticmethod
    def _case_text(case: dict) -> str:
        return " ".join(
            [
                str(case.get("summary", "")),
                str(case.get("classification", "")),
                " ".join(case.get("reasoning", [])),
                str(case.get("attributes", "")),
            ]
        )

