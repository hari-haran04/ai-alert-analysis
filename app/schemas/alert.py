from __future__ import annotations

from datetime import date

from pydantic import Field, field_validator

from app.schemas.common import CamelModel


class ThirdPartyIn(CamelModel):
    entity_id: str | None = Field(default=None, alias="entityId")
    name: str = Field(..., min_length=1, examples=["Gold Mayning 000"])
    country: str | None = None
    city: str | None = None
    date_of_birth: date | None = Field(default=None, alias="dateOfBirth")
    passport_number: str | None = Field(default=None, alias="passportNumber")
    passport: str | None = None
    registration_number: str | None = Field(default=None, alias="registrationNumber")
    tax_id: str | None = Field(default=None, alias="taxId")
    address: str | None = None
    aliases: list[str] = Field(default_factory=list)

    @field_validator("passport_number", mode="before")
    @classmethod
    def normalize_passport_alias(cls, value):
        return value


class HitIn(CamelModel):
    hit_id: str = Field(..., alias="hitId", examples=["HIT001"])
    name: str = Field(..., min_length=1)
    country: str | None = None
    city: str | None = None
    date_of_birth: date | None = Field(default=None, alias="dateOfBirth")
    passport_number: str | None = Field(default=None, alias="passportNumber")
    passport: str | None = None
    registration_number: str | None = Field(default=None, alias="registrationNumber")
    tax_id: str | None = Field(default=None, alias="taxId")
    address: str | None = None
    aliases: list[str] = Field(default_factory=list)
    score: float | None = Field(default=None, ge=0, le=100)
    level: str | None = Field(default=None, examples=["HIGH"])
    list_type: str | None = Field(default=None, alias="listType")
    source: str | None = None


class AlertIn(CamelModel):
    alert_id: str = Field(..., alias="alertId", examples=["ALT-1001"])
    screening_type: str = Field(..., alias="screeningType", examples=["SANCTIONS"])
    third_party: ThirdPartyIn = Field(..., alias="thirdParty")
    hits: list[HitIn] = Field(..., min_length=1)


class AlertStored(CamelModel):
    alert_id: str = Field(alias="alertId")
    screening_type: str = Field(alias="screeningType")
    third_party: ThirdPartyIn = Field(alias="thirdParty")
    hits: list[HitIn]

