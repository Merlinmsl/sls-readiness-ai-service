from abc import ABC, abstractmethod


class AIProviderError(RuntimeError):
    """Base exception for AI provider failures."""


class AIProviderConfigurationError(AIProviderError):
    """Raised when an AI provider is incorrectly configured."""


class AIProviderRequestError(AIProviderError):
    """Raised when a request to an AI provider fails."""


class AIProviderResponseError(AIProviderError):
    """Raised when an AI provider returns an unusable response."""


class BaseAIProvider(ABC):
    """Interface implemented by every AI provider."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the configured model identifier."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate a text response from a text prompt."""
        