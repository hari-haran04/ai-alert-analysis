from __future__ import annotations

import hashlib
import json


def stable_input_hash(payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

