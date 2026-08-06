from fastapi import APIRouter

from app.schemas.process import (
    ProcessAnalysisRequest,
    ProcessAnalysisResponse,
)
from app.services.process_analyzer import (
    analyze_manufacturing_process,
)


router = APIRouter(
    prefix="/process",
    tags=["Process"],
)


@router.post(
    "/analyze",
    response_model=ProcessAnalysisResponse,
    summary="Analyze manufacturing process steps",
)
def analyze_process(
    request: ProcessAnalysisRequest,
) -> ProcessAnalysisResponse:
    """Normalize process steps and request relevant evidence."""

    return analyze_manufacturing_process(request)