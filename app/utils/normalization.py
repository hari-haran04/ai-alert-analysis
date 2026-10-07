from __future__ import annotations

import re
import unicodedata
from datetime import date

COMPANY_SUFFIXES = {
    "ltd": "limited",
    "inc": "incorporated",
    "corp": "corporation",
    "co": "company",
    "jsc": "joint stock company",
    "ao": "joint stock company",
    "plc": "public limited company",
    "llc": "limited liability company",
}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^\w\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_name(value: str | None) -> str:
    normalized = normalize_text(value)
    tokens = [COMPANY_SUFFIXES.get(token, token) for token in normalized.split()]
    return " ".join(tokens)


def sorted_tokens(value: str | None) -> str:
    return " ".join(sorted(normalize_name(value).split()))


def normalize_identifier(value: str | None) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", value or "").upper()


def normalize_country(value: str | None) -> str:
    return normalize_text(value)


def normalize_date(value: date | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip()

