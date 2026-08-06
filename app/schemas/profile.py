from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.question import AdaptiveQuestion


class ProductCategory(StrEnum):
    """Food categories currently supported by the MVP."""

    BAKERY_PRODUCT = "bakery_product"
    PROCESSED_CONDIMENT = "processed_condiment"
    READY_TO_EAT_MEAL = "ready_to_eat_meal"
    OTHER = "other"


class ProductionScale(StrEnum):
    """Supported production scale answers."""

    HOME_KITCHEN = "home_kitchen"
    SMALL_FACILITY = "small_facility"
    MEDIUM_FACILITY = "medium_facility"


class PackagingType(StrEnum):
    """Packaging answers available on Page 1."""

    PLASTIC_CONTAINER = "plastic_container"
    GLASS_BOTTLE = "glass_bottle"
    FLEXIBLE_POUCH = "flexible_pouch"
    PAPER_OR_CARDBOARD = "paper_or_cardboard"
    OTHER = "other"


class StorageType(StrEnum):
    """Finished-product storage answers."""

    AMBIENT = "ambient"
    REFRIGERATED = "refrigerated"
    FROZEN = "frozen"


class ProfileAnalysisRequest(BaseModel):
    """Page 1 information submitted for product-profile analysis."""

    assessment_id: str = Field(
        min_length=3,
        max_length=64,
        examples=["ASM-1001"],
    )

    product_name: str = Field(
        min_length=2,
        max_length=120,
        examples=["Homemade chilli paste"],
    )

    product_category: ProductCategory
    production_scale: ProductionScale
    packaging_type: PackagingType
    storage_type: StorageType

    shelf_life_days: int = Field(
        ge=1,
        le=3650,
        examples=[90],
    )

    current_certifications: list[str] = Field(
        default_factory=list,
        max_length=5,
        examples=[[]],
    )

    other_details: str | None = Field(
        default=None,
        max_length=500,
        examples=["Produced twice per week"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "assessment_id": "ASM-1001",
                    "product_name": "Homemade chilli paste",
                    "product_category": "processed_condiment",
                    "production_scale": "home_kitchen",
                    "packaging_type": "glass_bottle",
                    "storage_type": "ambient",
                    "shelf_life_days": 90,
                    "current_certifications": [],
                    "other_details": "Produced twice per week",
                }
            ]
        }
    }


class NormalizedProductProfile(BaseModel):
    """Validated and normalized Page 1 product profile."""

    product_name: str
    product_category: ProductCategory
    production_scale: ProductionScale
    packaging_type: PackagingType
    storage_type: StorageType
    shelf_life_days: int
    current_certifications: list[str]
    assessment_tags: list[str]


class ProfileAnalysisResponse(BaseModel):
    """Result returned after Page 1 analysis."""

    assessment_id: str
    supported: bool
    unsupported_reason: str | None
    normalized_profile: NormalizedProductProfile
    selected_questions: list[AdaptiveQuestion]
    question_library_version: str
    selector_version: str