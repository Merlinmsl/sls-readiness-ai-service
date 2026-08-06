from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    service_name: str = "sls-readiness-ai-service"
    service_title: str = "SLS Readiness AI Service"
    service_version: str = "0.3.0"
    environment: str = "development"
    api_v1_prefix: str = "/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Create and cache one settings object for the application."""
    return Settings()