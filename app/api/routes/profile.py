from fastapi import APIRouter

from app.schemas.profile import (
    ProfileAnalysisRequest,
    ProfileAnalysisResponse,
)
from app.services.question_selector import analyze_product_profile


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.post(
    "/analyze",
    response_model=ProfileAnalysisResponse,
    summary="Analyze a Page 1 product profile",
)
def analyze_profile(
    request: ProfileAnalysisRequest,
) -> ProfileAnalysisResponse:
    """Validate a product profile and select follow-up questions."""

    return analyze_product_profile(request)