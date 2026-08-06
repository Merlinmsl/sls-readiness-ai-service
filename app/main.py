from fastapi import FastAPI

from app.api.router import api_v1_router, root_router
from app.core.config import get_settings


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    application = FastAPI(
        title=settings.service_title,
        description=(
            "AI-powered SLS readiness pre-assessment microservice "
            "for supported Sri Lankan food products."
        ),
        version=settings.service_version,
    )

    application.include_router(root_router)

    application.include_router(
        api_v1_router,
        prefix=settings.api_v1_prefix,
    )

    return application


app = create_application()