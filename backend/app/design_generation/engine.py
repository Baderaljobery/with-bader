from dataclasses import dataclass, field

from app.design_generation.base import ImageGenerator
from app.design_generation.models import (
    DesignAspectRatio,
    DesignPlatform,
    ReferenceImage,
    SlideImageOptions,
    SlideRole,
    SupportingContextItem,
)
from app.design_generation.prompts import build_slide_image_prompt
from app.design_generation.templates import (
    TemplateReferenceNotFoundError,
    load_template_reference_images,
)
from app.models.guest import Guest


class SlideImageGenerationError(Exception):
    """Base for slide-image-engine-layer failures that aren't already an
    ImageGenerationError subclass (currently just an unknown template)."""


@dataclass
class SlideImageRunResult:
    generator_provider: str
    generator_model: str | None
    prompt: str
    image_bytes: bytes
    mime_type: str


@dataclass
class SlideImageRequest:
    """Everything needed to generate ONE slide's visual - already resolved
    by the caller (design_service.py): no DB session, no guest lookup, no
    content-source resolution happens in this engine. Kept as a dataclass
    rather than threading ~10 positional args through generate_slide_image."""

    guest: Guest
    template_id: str
    role: SlideRole
    headline: str
    body_text: str
    platform: DesignPlatform
    aspect_ratio: DesignAspectRatio
    background_color: str
    accent_color: str
    custom_instructions: str | None = None
    supporting_context: list[SupportingContextItem] = field(default_factory=list)


class SlideImageGenerationEngine:
    """Generates the visual layer for ONE slide at a time. Multi-slide
    orchestration (looping over a design's slides, persisting each result)
    lives in app/services/design_service.py, not here - this class has no
    DB access at all."""

    def __init__(self, generator: ImageGenerator) -> None:
        self._generator = generator

    async def generate_slide_image(self, request: SlideImageRequest) -> SlideImageRunResult:
        try:
            reference_files = load_template_reference_images(request.template_id)
        except TemplateReferenceNotFoundError as exc:
            raise SlideImageGenerationError(str(exc)) from exc

        options = SlideImageOptions(
            platform=request.platform,
            template_id=request.template_id,
            role=request.role,
            aspect_ratio=request.aspect_ratio,
            background_color=request.background_color,
            accent_color=request.accent_color,
            reference_images=[
                ReferenceImage(data=data, mime_type=mime_type) for data, mime_type in reference_files
            ],
            custom_instructions=request.custom_instructions,
        )

        prompt = build_slide_image_prompt(
            request.guest, options, request.headline, request.body_text, request.supporting_context
        )

        image_result = await self._generator.generate(prompt, options)

        return SlideImageRunResult(
            generator_provider=self._generator.provider_name,
            generator_model=self._generator.model_name,
            prompt=prompt,
            image_bytes=image_result.image_bytes,
            mime_type=image_result.mime_type,
        )


def get_slide_image_engine() -> SlideImageGenerationEngine:
    from app.design_generation.factory import build_image_generator

    return SlideImageGenerationEngine(generator=build_image_generator())
