from __future__ import annotations

from pydantic import Field

from app.schemas.common import CamelModel


class RuleConfig(CamelModel):
    version: str
    weights: dict[str, float]
    thresholds: dict[str, float]
    priorities: dict[str, str]
    rules: list[dict] = Field(default_factory=list)
    risk: dict = Field(default_factory=dict)

