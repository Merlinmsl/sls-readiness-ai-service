from google import genai

from app.providers.base import (
    AIProviderConfigurationError,
    AIProviderRequestError,
    AIProviderResponseError,
    BaseAIProvider,
)


class GeminiAIProvider(BaseAIProvider):
    """Google Gemini implementation of the AI provider interface."""

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        cleaned_api_key = api_key.strip()
        cleaned_model = model.strip()

        if not cleaned_api_key:
            raise AIProviderConfigurationError(
                "Gemini API key is missing."
            )

        if not cleaned_model:
            raise AIProviderConfigurationError(
                "Gemini model name is missing."
            )

        self._model = cleaned_model
        self._client = genai.Client(
            api_key=cleaned_api_key,
        )

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    def generate_text(self, prompt: str) -> str:
        """Send a text request to Gemini and return its text output."""

        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            raise ValueError("Prompt cannot be empty.")

        try:
            interaction = self._client.interactions.create(
                model=self._model,
                input=cleaned_prompt,
            )
        except Exception as error:
            raise AIProviderRequestError(
                "The Gemini API request failed."
            ) from error

        response_text = (
            interaction.output_text or ""
        ).strip()

        if not response_text:
            raise AIProviderResponseError(
                "Gemini returned an empty response."
            )

        return response_text