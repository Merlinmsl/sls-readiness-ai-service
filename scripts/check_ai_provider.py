from app.providers.base import AIProviderError
from app.providers.factory import get_ai_provider


def main() -> None:
    """Perform one controlled AI provider request."""

    provider = get_ai_provider()

    print(
        f"Provider: {provider.provider_name}"
    )
    print(
        f"Model: {provider.model_name}"
    )

    try:
        response = provider.generate_text(
            "Reply with only this exact text: "
            "AI connection successful"
        )
    except AIProviderError as error:
        print(
            f"Connection failed: {error}"
        )
        raise SystemExit(1) from error

    print(
        f"Response: {response}"
    )


if __name__ == "__main__":
    main()
    