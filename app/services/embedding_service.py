from __future__ import annotations

import hashlib
import math
from functools import lru_cache

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        if self.settings.enable_sentence_transformers:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.settings.embedding_model)
            except Exception:
                self._model = None

    def embed(self, text: str) -> list[float]:
        if self._model is not None:
            vector = self._model.encode(text, normalize_embeddings=True)
            return [float(item) for item in vector]
        return self._hash_embedding(text, self.settings.embedding_dimension)

    @staticmethod
    def _hash_embedding(text: str, dimensions: int) -> list[float]:
        buckets = [0.0] * dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            buckets[idx] += sign
        norm = math.sqrt(sum(value * value for value in buckets)) or 1.0
        return [round(value / norm, 6) for value in buckets]

    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        dot = sum(left[i] * right[i] for i in range(size))
        left_norm = math.sqrt(sum(value * value for value in left[:size]))
        right_norm = math.sqrt(sum(value * value for value in right[:size]))
        if not left_norm or not right_norm:
            return 0.0
        return max(0.0, min(1.0, dot / (left_norm * right_norm)))


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

