from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.ai import AIStatusResponse
from app.services.ai_status_service import build_ai_status


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.get(
    "/status",
    response_model=AIStatusResponse,
    summary="Check AI provider configuration",
)
def get_ai_status(
    settings: Annotated[
        Settings,
        Depends(get_settings),
    ],
) -> AIStatusResponse:
    """Return AI configuration without performing a live request."""

    return build_ai_status(settings)
