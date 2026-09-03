import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.content.generation.base import ContentGenerator
from app.content.generation.context_builder import build_content_context, has_meaningful_context
from app.content.generation.models import ContentContextItem, ContentGenerationOptions
from app.models.guest import Guest
from app.services import guest_service


class ContentContextInsufficientError(Exception):
    """Raised when a guest has no meaningful grounding context yet (no
    answered questions, notebook content, transcript, or research). Content
    generation must never fall back to generic filler in this case."""


@dataclass
class ContentGenerationRunResult:
    guest: Guest
    generator_provider: str
    generator_model: str | None
    title: str | None
    content: str
    context_items: list[ContentContextItem]


class ContentGenerationEngine:
    """Orchestrates guest lookup, context building, and generation -
    vendor-agnostic, depends only on ContentGenerator. Never touches
    Exa/Tavily/Groq directly, and never persists anything (preview only -
    see app/services/content_service.py for the explicit save step)."""

    def __init__(self, generator: ContentGenerator) -> None:
        self._generator = generator

    async def generate_content(
        self, guest_id: uuid.UUID, db: Session, options: ContentGenerationOptions
    ) -> ContentGenerationRunResult:
        guest = guest_service.get_guest_by_id(db, guest_id)

        context_items = build_content_context(db, guest_id)
        if not has_meaningful_context(context_items):
            raise ContentContextInsufficientError(
                f"Guest '{guest_id}' does not have enough answered questions, notebook content, "
                "transcript, or research yet to generate grounded content"
            )

        result = await self._generator.generate(guest, context_items, options)

        return ContentGenerationRunResult(
            guest=guest,
            generator_provider=self._generator.provider_name,
            generator_model=self._generator.model_name,
            title=result.title,
            content=result.content,
            context_items=context_items,
        )


def get_content_generation_engine() -> ContentGenerationEngine:
    """Single wiring point for the generator implementation. Swap via
    CONTENT_GENERATOR_PROVIDER - ContentGenerationEngine itself never
    changes."""
    from app.content.generation.factory import build_content_generator

    return ContentGenerationEngine(generator=build_content_generator())
