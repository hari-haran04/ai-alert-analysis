from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Classification(StrEnum):
    TRUE_ALERT = "TRUE_ALERT"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INCONCLUSIVE = "INCONCLUSIVE"


class MatchResult(StrEnum):
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISMATCH = "MISMATCH"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
    )


class ErrorResponse(CamelModel):
    error: dict = Field(
        examples=[
            {
                "code": "INVALID_ALERT",
                "message": "The alert payload is invalid",
                "requestId": "REQ-123",
            }
        ]
    )

