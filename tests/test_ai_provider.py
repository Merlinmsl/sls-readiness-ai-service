import pytest

from app.core.config import Settings
from app.providers.base import (
    AIProviderConfigurationError,
)
from app.providers.factory import create_ai_provider
from app.providers.mock_provider import MockAIProvider


def test_mock_provider_returns_deterministic_response() -> None:
    provider = MockAIProvider()

    response = provider.generate_text(
        "Test the provider."
    )

    assert provider.provider_name == "mock"
    assert provider.model_name == "mock-model-v1"
    assert (
        response
        == "Mock AI response generated successfully."
    )


def test_mock_provider_rejects_empty_prompt() -> None:
    provider = MockAIProvider()

    with pytest.raises(ValueError):
        provider.generate_text("   ")


def test_factory_creates_mock_provider() -> None:
    settings = Settings(
        _env_file=None,
        ai_provider="mock",
    )

    provider = create_ai_provider(settings)

    assert isinstance(provider, MockAIProvider)


def test_gemini_provider_requires_api_key() -> None:
    settings = Settings(
        _env_file=None,
        ai_provider="gemini",
        gemini_api_key=None,
    )

    with pytest.raises(
        AIProviderConfigurationError
    ):
        create_ai_provider(settings)
        