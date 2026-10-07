from __future__ import annotations

from app.services.case_retrieval import CaseRetrievalService
from scripts.seed_data import seed


if __name__ == "__main__":
    seed()
    print(f"Seeded embeddings for {len(CaseRetrievalService().similar_cases('sanctions match', 100))} cases")

