from __future__ import annotations

from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover - fallback for minimal local envs
    fuzz = None

from app.utils.normalization import normalize_name, normalize_text, sorted_tokens


def ratio(left: str | None, right: str | None) -> float:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return 0.0
    if fuzz:
        return fuzz.ratio(left_norm, right_norm) / 100
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def token_sort_ratio(left: str | None, right: str | None) -> float:
    return ratio(sorted_tokens(left), sorted_tokens(right))


def token_set_ratio(left: str | None, right: str | None) -> float:
    left_set = set(normalize_name(left).split())
    right_set = set(normalize_name(right).split())
    if not left_set or not right_set:
        return 0.0
    if fuzz:
        return fuzz.token_set_ratio(" ".join(left_set), " ".join(right_set)) / 100
    return len(left_set & right_set) / len(left_set | right_set)


def jaro_winkler(left: str | None, right: str | None) -> float:
    return ratio(left, right)


def levenshtein_similarity(left: str | None, right: str | None) -> float:
    return ratio(left, right)


def weighted_name_similarity(
    left: str | None, right: str | None, embedding_similarity: float = 0.0
) -> float:
    if normalize_name(left) == normalize_name(right) and left and right:
        return 1.0
    exact = 0.0
    scores = [
        exact,
        ratio(left, right),
        token_sort_ratio(left, right),
        token_set_ratio(left, right),
        jaro_winkler(left, right),
        levenshtein_similarity(left, right),
        embedding_similarity,
    ]
    weights = [0.18, 0.18, 0.16, 0.18, 0.1, 0.1, 0.1]
    return round(sum(score * weight for score, weight in zip(scores, weights)), 4)

