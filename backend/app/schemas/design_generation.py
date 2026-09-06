import uuid

from pydantic import BaseModel, Field, field_validator, model_validator

from app.design_planning.content_limits import TEMPLATE_IDS
from app.schemas.design_draft import HEX_COLOR_PATTERN, DesignAspectRatio, DesignPlatform
from app.schemas.design_slide import SlideRole


def _validate_slide_indices(slide_count: int, indices: list[int]) -> None:
    if len(indices) != slide_count:
        raise ValueError(f"Expected exactly {slide_count} slide(s), got {len(indices)}")
    if sorted(indices) != list(range(1, slide_count + 1)):
        raise ValueError(f"Slide indices must be exactly 1..{slide_count} with no duplicates")


def _validate_template_id(template_id: str) -> str:
    if template_id not in TEMPLATE_IDS:
        raise ValueError(f"Unknown design template '{template_id}' (known: {', '.join(TEMPLATE_IDS)})")
    return template_id


class SlideRoleAssignment(BaseModel):
    index: int = Field(ge=1, le=5)
    role: SlideRole


class DesignPlanRequest(BaseModel):
    """Step 1 of the flow: turn user-selected sources + user-chosen slide
    count/roles into a structured text preview - no image is generated
    here, and nothing is persisted (mirrors Content Creation's own
    preview-first /generate). See app/design_planning/."""

    content_draft_id: uuid.UUID | None = None
    question_ids: list[uuid.UUID] = Field(default_factory=list)
    notebook_block_ids: list[uuid.UUID] = Field(default_factory=list)

    template_id: str
    slide_count: int = Field(ge=1, le=5)
    slide_roles: list[SlideRoleAssignment]

    platform: DesignPlatform
    custom_instructions: str | None = Field(default=None, max_length=1000)

    _validate_template = field_validator("template_id")(_validate_template_id)

    @model_validator(mode="after")
    def _check_roles_match_count(self) -> "DesignPlanRequest":
        _validate_slide_indices(self.slide_count, [item.index for item in self.slide_roles])
        return self


class PlannedSlide(BaseModel):
    index: int = Field(ge=1, le=5)
    role: SlideRole
    headline: str
    body_text: str
    cta_text: str | None = None


class DesignPlanResponse(BaseModel):
    guest_id: uuid.UUID
    template_id: str
    slide_count: int
    slides: list[PlannedSlide]
    sources_used: list[str] = Field(default_factory=list)
    ai_provider: str
    ai_model: str | None = None


class DesignSlideInput(BaseModel):
    """One slide's approved/edited structure, submitted when creating the
    persisted design set (see DesignCreateRequest) - this is the text the
    user reviewed in the structure-preview step, not necessarily identical
    to what the planner first produced."""

    index: int = Field(ge=1, le=5)
    role: SlideRole
    headline: str = Field(min_length=1)
    body_text: str
    cta_text: str | None = None


class DesignCreateRequest(BaseModel):
    """Step 2: persist the approved slide structure (still no images yet -
    see POST /api/designs/{design_id}/generate)."""

    content_draft_id: uuid.UUID | None = None
    question_ids: list[uuid.UUID] = Field(default_factory=list)
    notebook_block_ids: list[uuid.UUID] = Field(default_factory=list)

    template_id: str
    slide_count: int = Field(ge=1, le=5)
    slides: list[DesignSlideInput]

    platform: DesignPlatform
    aspect_ratio: DesignAspectRatio = "1:1"
    background_color: str = Field(default="#FFFFFF", pattern=HEX_COLOR_PATTERN)
    accent_color: str = Field(default="#1B8FEA", pattern=HEX_COLOR_PATTERN)
    title: str | None = None
    custom_instructions: str | None = Field(default=None, max_length=1000)

    _validate_template = field_validator("template_id")(_validate_template_id)

    @model_validator(mode="after")
    def _check_slides_match_count(self) -> "DesignCreateRequest":
        _validate_slide_indices(self.slide_count, [item.index for item in self.slides])
        return self
