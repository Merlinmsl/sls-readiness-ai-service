import json
from functools import lru_cache
from pathlib import Path

from app.schemas.profile import (
    NormalizedProductProfile,
    ProductCategory,
    ProfileAnalysisRequest,
    ProfileAnalysisResponse,
)
from app.schemas.question import (
    AdaptiveQuestion,
    QuestionLibrary,
)


KNOWLEDGE_DIRECTORY = Path(__file__).resolve().parent.parent / "knowledge"
QUESTION_LIBRARY_FILE = KNOWLEDGE_DIRECTORY / "questions.json"

MAX_PROFILE_QUESTIONS = 6
SELECTOR_VERSION = "rules-v1"


@lru_cache(maxsize=1)
def load_question_library() -> QuestionLibrary:
    """Load and validate the question library once."""

    raw_content = QUESTION_LIBRARY_FILE.read_text(encoding="utf-8")
    parsed_content = json.loads(raw_content)

    return QuestionLibrary.model_validate(parsed_content)


def normalize_text(value: str) -> str:
    """Remove unnecessary whitespace while preserving the user's wording."""

    return " ".join(value.split())


def normalize_certifications(certifications: list[str]) -> list[str]:
    """Remove blank and duplicate certification values."""

    normalized: list[str] = []

    for certification in certifications:
        cleaned_value = normalize_text(certification)

        if cleaned_value and cleaned_value not in normalized:
            normalized.append(cleaned_value)

    return normalized


def build_assessment_tags(
    request: ProfileAnalysisRequest,
) -> set[str]:
    """Convert Page 1 answers into tags used by the selector."""

    tags = {
        "all",
        f"category:{request.product_category.value}",
        f"scale:{request.production_scale.value}",
        f"packaging:{request.packaging_type.value}",
        f"storage:{request.storage_type.value}",
    }

    if request.shelf_life_days <= 7:
        tags.add("shelf_life:short")
    elif request.shelf_life_days <= 30:
        tags.add("shelf_life:medium")
    else:
        tags.add("shelf_life:extended")

    if request.current_certifications:
        tags.add("certification:present")
    else:
        tags.add("certification:none")

    return tags


def select_questions(
    assessment_tags: set[str],
) -> tuple[list[AdaptiveQuestion], str]:
    """Select relevant questions from the validated question library."""

    library = load_question_library()

    matching_questions = [
        question
        for question in library.questions
        if assessment_tags.intersection(question.trigger_tags)
    ]

    matching_questions.sort(
        key=lambda question: (
            question.priority,
            question.id,
        )
    )

    selected_questions = [
        AdaptiveQuestion(
            id=question.id,
            text=question.text,
            type=question.type,
            options=question.options,
            requirement_ids=question.requirement_ids,
        )
        for question in matching_questions[:MAX_PROFILE_QUESTIONS]
    ]

    return selected_questions, library.version


def analyze_product_profile(
    request: ProfileAnalysisRequest,
) -> ProfileAnalysisResponse:
    """Analyze Page 1 answers and select adaptive questions."""

    assessment_tags = build_assessment_tags(request)

    normalized_profile = NormalizedProductProfile(
        product_name=normalize_text(request.product_name),
        product_category=request.product_category,
        production_scale=request.production_scale,
        packaging_type=request.packaging_type,
        storage_type=request.storage_type,
        shelf_life_days=request.shelf_life_days,
        current_certifications=normalize_certifications(
            request.current_certifications
        ),
        assessment_tags=sorted(
            tag for tag in assessment_tags if tag != "all"
        ),
    )

    if request.product_category == ProductCategory.OTHER:
        return ProfileAnalysisResponse(
            assessment_id=request.assessment_id,
            supported=False,
            unsupported_reason=(
                "This food product category is not supported "
                "by the current MVP."
            ),
            normalized_profile=normalized_profile,
            selected_questions=[],
            question_library_version=load_question_library().version,
            selector_version=SELECTOR_VERSION,
        )

    selected_questions, library_version = select_questions(
        assessment_tags
    )

    return ProfileAnalysisResponse(
        assessment_id=request.assessment_id,
        supported=True,
        unsupported_reason=None,
        normalized_profile=normalized_profile,
        selected_questions=selected_questions,
        question_library_version=library_version,
        selector_version=SELECTOR_VERSION,
    )
    
    