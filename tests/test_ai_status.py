from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


client = TestClient(app)


def get_mock_test_settings() -> Settings:
    """Return isolated settings for this test."""

    return Settings(
        _env_file=None,
        service_version="0.5.0",
        environment="testing",
        ai_provider="mock",
        gemini_api_key=None,
    )


def test_ai_status_returns_mock_configuration() -> None:
    app.dependency_overrides[get_settings] = (
        get_mock_test_settings
    )

    try:
        response = client.get("/v1/ai/status")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == {
        "provider": "mock",
        "configured": True,
        "model": "mock-model-v1",
        "live_request_performed": False,
    }
    