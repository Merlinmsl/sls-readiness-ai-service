from app.providers.base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    """Deterministic provider used for tests and fallback behavior."""

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-model-v1"

    def generate_text(self, prompt: str) -> str:
        """Return a predictable response without calling an API."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        return "Mock AI response generated successfully."