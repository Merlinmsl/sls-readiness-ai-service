from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse


router = APIRouter(
    tags=["System"],
)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check service health",
)
def health_check(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Return the current health and configuration of the service."""

    return HealthResponse(
        status="healthy",
        service=settings.service_name,
        version=settings.service_version,
        environment=settings.environment,
    )
    
    