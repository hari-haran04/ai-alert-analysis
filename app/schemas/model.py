from __future__ import annotations

from pydantic import Field

from app.schemas.common import CamelModel


class ModelMetadata(CamelModel):
    model_name: str = Field(alias="modelName")
    model_version: str = Field(alias="modelVersion")
    training_dataset_version: str = Field(alias="trainingDatasetVersion")
    trained_at: str | None = Field(default=None, alias="trainedAt")
    features: list[str]
    metrics: dict
    loaded: bool

