from enum import StrEnum

from pydantic import BaseModel, Field


class QuestionType(StrEnum):
    """Question types supported by the assessment interface."""

    SINGLE_SELECT = "single_select"


class QuestionOption(BaseModel):
    """One selectable answer displayed to the user."""

    value: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=160)


class QuestionDefinition(BaseModel):
    """Internal question definition stored in the knowledge base."""

    id: str = Field(min_length=3, max_length=80)
    text: str = Field(min_length=5, max_length=300)
    type: QuestionType
    options: list[QuestionOption] = Field(min_length=2, max_length=8)
    trigger_tags: list[str] = Field(min_length=1)
    priority: int = Field(ge=1, le=100)
    requirement_ids: list[str] = Field(default_factory=list)


class QuestionLibrary(BaseModel):
    """Validated structure of the questions knowledge file."""

    version: str
    questions: list[QuestionDefinition]


class AdaptiveQuestion(BaseModel):
    """Question information returned to the main application."""

    id: str
    text: str
    type: QuestionType
    options: list[QuestionOption]
    requirement_ids: list[str]