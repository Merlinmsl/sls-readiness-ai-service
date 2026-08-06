from functools import lru_cache

from app.core.config import Settings, get_settings
from app.providers.base import (
    AIProviderConfigurationError,
    BaseAIProvider,
)
from app.providers.gemini_provider import GeminiAIProvider
from app.providers.mock_provider import MockAIProvider


def create_ai_provider(
    settings: Settings,
) -> BaseAIProvider:
    """Create the configured AI provider."""

    if settings.ai_provider == "mock":
        return MockAIProvider()

    if settings.ai_provider == "gemini":
        if settings.gemini_api_key is None:
            raise AIProviderConfigurationError(
                "GEMINI_API_KEY is required when "
                "AI_PROVIDER is set to gemini."
            )

        return GeminiAIProvider(
            api_key=(
                settings.gemini_api_key.get_secret_value()
            ),
            model=settings.gemini_model,
        )

    raise AIProviderConfigurationError(
        f"Unsupported AI provider: {settings.ai_provider}"
    )


@lru_cache(maxsize=1)
def get_ai_provider() -> BaseAIProvider:
    """Create and cache the configured provider."""

    return create_ai_provider(get_settings())



