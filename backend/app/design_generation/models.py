from typing import Literal

from pydantic import BaseModel

DesignPlatform = Literal["linkedin", "x", "instagram", "general"]
DesignAspectRatio = Literal["1:1", "4:5", "16:9", "9:16"]
SlideRole = Literal["cover", "main_content", "continuation", "quote", "quick_points", "closing"]


class SupportingContextItem(BaseModel):
    """A single user-selected question/answer pair used as supporting
    context. Only ever built from ANSWERED questions - see
    app/design_planning/context.py."""

    id: str
    question: str
    answer: str


class ReferenceImage(BaseModel):
    """A real reference image's raw bytes, read server-side from the
    selected template's registry entry (see templates.py) - never a
    filename/description standing in for the actual image."""

    data: bytes
    mime_type: str


class SlideImageOptions(BaseModel):
    """Everything the image layer needs for ONE slide. Distinct from the
    old single-slide DesignGenerationOptions: role replaces layout_type
    (composition now varies by the template + the slide's role, not a
    generic 4-way layout enum), and reference_images carries the selected
    template's actual reference bytes."""

    platform: DesignPlatform
    template_id: str
    role: SlideRole
    aspect_ratio: DesignAspectRatio
    background_color: str
    accent_color: str
    reference_images: list[ReferenceImage]
    custom_instructions: str | None = None


class ImageGenerationResult(BaseModel):
    image_bytes: bytes
    mime_type: str
