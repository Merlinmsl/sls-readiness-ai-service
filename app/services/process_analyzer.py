import json
import re
from functools import lru_cache
from pathlib import Path

from app.schemas.process import (
    EvidenceRequest,
    EvidenceRequestRule,
    NormalizedProcessStep,
    ProcessAnalysisRequest,
    ProcessAnalysisResponse,
    ProcessRuleLibrary,
    StageRule,
)


KNOWLEDGE_DIRECTORY = Path(__file__).resolve().parent.parent / "knowledge"
PROCESS_RULE_LIBRARY_FILE = (
    KNOWLEDGE_DIRECTORY / "process_rules.json"
)

MAX_PHOTO_REQUESTS = 5
MAX_DOCUMENT_REQUESTS = 2
ANALYZER_VERSION = "rules-v1"


@lru_cache(maxsize=1)
def load_process_rule_library() -> ProcessRuleLibrary:
    """Load and validate process and evidence rules."""

    raw_content = PROCESS_RULE_LIBRARY_FILE.read_text(
        encoding="utf-8"
    )
    parsed_content = json.loads(raw_content)

    return ProcessRuleLibrary.model_validate(parsed_content)


def normalize_process_text(value: str) -> str:
    """Normalize whitespace without changing user meaning."""

    return " ".join(value.split())


def contains_keyword(
    normalized_text: str,
    keyword: str,
) -> bool:
    """Check for a keyword using case-insensitive word boundaries."""

    pattern = rf"\b{re.escape(keyword.casefold())}\b"

    return re.search(
        pattern,
        normalized_text.casefold(),
    ) is not None


def classify_process_step(
    process_step: str,
    stage_rules: list[StageRule],
) -> tuple[str, str, str | None]:
    """Map one user step to the first matching standard stage."""

    ordered_rules = sorted(
        stage_rules,
        key=lambda rule: (
            rule.priority,
            rule.stage_id,
        ),
    )

    for stage_rule in ordered_rules:
        for keyword in stage_rule.keywords:
            if contains_keyword(process_step, keyword):
                return (
                    stage_rule.stage_id,
                    stage_rule.stage_label,
                    keyword,
                )

    return (
        "unclassified",
        "Unclassified process step",
        None,
    )


def build_process_tags(
    request: ProcessAnalysisRequest,
    normalized_steps: list[NormalizedProcessStep],
) -> set[str]:
    """Build tags from the profile and classified process."""

    tags = {
        "all",
        f"category:{request.profile.product_category.value}",
        f"packaging:{request.profile.packaging_type.value}",
        f"storage:{request.profile.storage_type.value}",
        f"scale:{request.profile.production_scale.value}",
    }

    for normalized_step in normalized_steps:
        if normalized_step.stage_id != "unclassified":
            tags.add(
                f"stage:{normalized_step.stage_id}"
            )

    return tags


def select_evidence_requests(
    rules: list[EvidenceRequestRule],
    process_tags: set[str],
    maximum_requests: int,
) -> list[EvidenceRequest]:
    """Select and prioritize relevant evidence requests."""

    matching_rules = [
        rule
        for rule in rules
        if process_tags.intersection(rule.trigger_tags)
    ]

    matching_rules.sort(
        key=lambda rule: (
            rule.priority,
            rule.id,
        )
    )

    return [
        EvidenceRequest(
            id=rule.id,
            title=rule.title,
            instruction=rule.instruction,
            reason=rule.reason,
            required=rule.required,
        )
        for rule in matching_rules[:maximum_requests]
    ]


def analyze_manufacturing_process(
    request: ProcessAnalysisRequest,
) -> ProcessAnalysisResponse:
    """Analyze Page 2 manufacturing steps."""

    library = load_process_rule_library()

    normalized_steps: list[NormalizedProcessStep] = []

    for index, process_step in enumerate(
        request.process_steps,
        start=1,
    ):
        normalized_text = normalize_process_text(process_step)

        stage_id, stage_label, matched_keyword = (
            classify_process_step(
                normalized_text,
                library.stage_rules,
            )
        )

        normalized_steps.append(
            NormalizedProcessStep(
                sequence=index,
                original_text=process_step,
                normalized_text=normalized_text,
                stage_id=stage_id,
                stage_label=stage_label,
                matched_keyword=matched_keyword,
            )
        )

    process_tags = build_process_tags(
        request,
        normalized_steps,
    )

    photo_requests = select_evidence_requests(
        rules=library.photo_requests,
        process_tags=process_tags,
        maximum_requests=MAX_PHOTO_REQUESTS,
    )

    document_requests = select_evidence_requests(
        rules=library.document_requests,
        process_tags=process_tags,
        maximum_requests=MAX_DOCUMENT_REQUESTS,
    )

    unclassified_step_count = sum(
        step.stage_id == "unclassified"
        for step in normalized_steps
    )

    visible_process_tags = sorted(
        tag
        for tag in process_tags
        if tag.startswith("stage:")
    )

    return ProcessAnalysisResponse(
        assessment_id=request.assessment_id,
        normalized_steps=normalized_steps,
        process_tags=visible_process_tags,
        photo_requests=photo_requests,
        document_requests=document_requests,
        unclassified_step_count=unclassified_step_count,
        rule_library_version=library.version,
        analyzer_version=ANALYZER_VERSION,
    )