import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.models.guest_research import GuestResearch
from app.questions.generation.base import QuestionGenerator
from app.questions.generation.models import GeneratedQuestionItem, QuestionGenerationOptions
from app.questions.generation.research_context import build_research_context
from app.services import guest_research_service, guest_service


class QuestionGenerationResearchMissingError(Exception):
    """Raised when a guest has no GuestResearch yet - question generation
    requires completed research first."""


@dataclass
class QuestionGenerationRunResult:
    guest: Guest
    research: GuestResearch
    generator_provider: str
    generator_model: str | None
    requested_count: int
    generated_count: int
    questions: list[GeneratedQuestionItem]


class QuestionGenerationEngine:
    """Orchestrates guest + latest-research lookup, compact research-context
    building, and generation - vendor-agnostic, depends only on
    QuestionGenerator. Never touches Exa/Tavily/GuestResearch.sources."""

    def __init__(self, generator: QuestionGenerator) -> None:
        self._generator = generator

    async def generate_questions(
        self, guest_id: uuid.UUID, db: Session, options: QuestionGenerationOptions
    ) -> QuestionGenerationRunResult:
        guest = guest_service.get_guest_by_id(db, guest_id)

        research = guest_research_service.get_latest_guest_research(db, guest_id)
        if research is None:
            raise QuestionGenerationResearchMissingError(
                f"Guest '{guest_id}' has no guest research yet - run research before "
                "generating questions"
            )

        research_items = build_research_context(research)

        result = await self._generator.generate(guest, research_items, options)

        return QuestionGenerationRunResult(
            guest=guest,
            research=research,
            generator_provider=self._generator.provider_name,
            generator_model=self._generator.model_name,
            requested_count=options.count,
            generated_count=len(result.questions),
            questions=result.questions,
        )


def get_question_generation_engine() -> QuestionGenerationEngine:
    """Single wiring point for the generator implementation. Swap via
    QUESTION_GENERATOR_PROVIDER - QuestionGenerationEngine itself never
    changes."""
    from app.questions.generation.factory import build_question_generator

    return QuestionGenerationEngine(generator=build_question_generator())
