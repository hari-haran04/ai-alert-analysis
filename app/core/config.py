from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI-Assisted Alert Analysis"
    app_env: Literal["development", "test", "production"] = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@postgres:5432/alert_analysis"
    )
    redis_url: str = "redis://redis:6379/0"

    llm_provider: Literal["local", "openai", "azure_openai"] = "local"
    llm_model: str = "GPT-5.6"
    openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None

    embedding_model: str = "BAAI/bge-m3"
    embedding_dimension: int = 1024
    enable_sentence_transformers: bool = False

    model_path: str = "ml/models/entity_matcher.joblib"
    rule_version: str = "1.0.0"
    rule_config_path: str = "rules/matching_rules.yaml"

    api_key: str = "dev-api-key"
    auth_enabled: bool = Field(default=False, description="Enable API key auth.")
    rate_limit_per_minute: int = 120
    log_level: str = "INFO"

    def resolve_project_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return PROJECT_ROOT.parent / path


@lru_cache
def get_settings() -> Settings:
    return Settings()

