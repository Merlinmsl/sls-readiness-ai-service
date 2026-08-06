from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.schemas.profile import NormalizedProductProfile


ProcessStepText = Annotated[
    str,
    Field(
        min_length=2,
        max_length=200,
    ),
]


class ProcessAnalysisRequest(BaseModel):
    """Page 2 manufacturing-process information."""

    assessment_id: str = Field(
        min_length=3,
        max_length=64,
        examples=["ASM-1001"],
    )

    profile: NormalizedProductProfile

    process_steps: list[ProcessStepText] = Field(
        min_length=1,
        max_length=5,
    )

    additional_details: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("process_steps")
    @classmethod
    def validate_process_steps(
        cls,
        process_steps: list[str],
    ) -> list[str]:
        """Trim steps and reject blank or duplicate entries."""

        cleaned_steps: list[str] = []
        seen_steps: set[str] = set()

        for process_step in process_steps:
            cleaned_step = " ".join(process_step.split())

            if not cleaned_step:
                raise ValueError(
                    "Process steps cannot be blank."
                )

            comparison_value = cleaned_step.casefold()

            if comparison_value in seen_steps:
                raise ValueError(
                    "Duplicate process steps are not allowed."
                )

            seen_steps.add(comparison_value)
            cleaned_steps.append(cleaned_step)

        return cleaned_steps


class StageRule(BaseModel):
    """One deterministic process-classification rule."""

    stage_id: str
    stage_label: str
    keywords: list[str]
    priority: int


class EvidenceRequestRule(BaseModel):
    """Internal rule for requesting a photo or document."""

    id: str
    title: str
    instruction: str
    reason: str
    trigger_tags: list[str]
    priority: int
    required: bool


class ProcessRuleLibrary(BaseModel):
    """Validated process rule knowledge file."""

    version: str
    stage_rules: list[StageRule]
    photo_requests: list[EvidenceRequestRule]
    document_requests: list[EvidenceRequestRule]


class NormalizedProcessStep(BaseModel):
    """One user process step mapped to a standard stage."""

    sequence: int
    original_text: str
    normalized_text: str
    stage_id: str
    stage_label: str
    matched_keyword: str | None


class EvidenceRequest(BaseModel):
    """Photo or document request returned to the application."""

    id: str
    title: str
    instruction: str
    reason: str
    required: bool


class ProcessAnalysisResponse(BaseModel):
    """Result returned after Page 2 process analysis."""

    assessment_id: str
    normalized_steps: list[NormalizedProcessStep]
    process_tags: list[str]
    photo_requests: list[EvidenceRequest]
    document_requests: list[EvidenceRequest]
    unclassified_step_count: int
    rule_library_version: str
    analyzer_version: str