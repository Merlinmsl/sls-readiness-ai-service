from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    service_name: str = "sls-readiness-ai-service"
    service_title: str = "SLS Readiness AI Service"
    service_version: str = "0.5.0"
    environment: str = "development"
    api_v1_prefix: str = "/v1"

    ai_provider: Literal["mock", "gemini"] = "mock"

    gemini_api_key: SecretStr | None = None

    gemini_model: str = Field(
        default="gemini-3.6-flash",
        min_length=3,
        max_length=100,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Create and cache one settings object."""

    return Settings()