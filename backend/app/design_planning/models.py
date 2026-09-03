from typing import Literal

from pydantic import BaseModel

DesignPlatform = Literal["linkedin", "x", "instagram", "general"]
SlideRole = Literal["cover", "main_content", "continuation", "quote", "quick_points", "closing"]
PlanContextCategory = Literal["content_draft", "answers", "notebook"]


class PlanContextItem(BaseModel):
    """A single real, already-selected source item. Unlike Content
    Creation's context builder, there is no "topic hint only" category here
    - everything that reaches the planner is either the saved content draft
    itself, an explicitly-selected ANSWERED question, or explicitly-
    selected real notebook text. See context.py."""

    id: str
    category: PlanContextCategory
    text: str


class SlideRoleSpec(BaseModel):
    index: int
    role: SlideRole


class SlidePlanningOptions(BaseModel):
    platform: DesignPlatform
    slide_roles: list[SlideRoleSpec]
    # Which renderer this content is being written for - drives the exact
    # per-slide character budgets in the prompt (see content_limits.py).
    # The planner never chooses this; it is always the user's own template
    # selection, passed straight through.
    template_id: str
    custom_instructions: str | None = None
    language: str = "ar"


class PlannedSlideResult(BaseModel):
    index: int
    role: SlideRole
    headline: str
    body_text: str
    cta_text: str | None = None


class SlidePlanGenerationResult(BaseModel):
    slides: list[PlannedSlideResult]
