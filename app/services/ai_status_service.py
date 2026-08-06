from app.core.config import Settings
from app.schemas.ai import AIStatusResponse


def build_ai_status(
    settings: Settings,
) -> AIStatusResponse:
    """Build a status response without making an external API call."""

    if settings.ai_provider == "mock":
        return AIStatusResponse(
            provider="mock",
            configured=True,
            model="mock-model-v1",
            live_request_performed=False,
        )

    key_is_configured = (
        settings.gemini_api_key is not None
        and bool(
            settings.gemini_api_key
            .get_secret_value()
            .strip()
        )
    )

    return AIStatusResponse(
        provider="gemini",
        configured=key_is_configured,
        model=settings.gemini_model,
        live_request_performed=False,
    )
    
    