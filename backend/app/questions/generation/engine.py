import math
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.guest import Guest
from app.models.guest_research import GuestResearch
from app.models.question import Question
from app.questions.generation.base import QuestionGenerator
from app.questions.generation.deduplication import (
    filter_unique_candidates,
    select_diverse_questions,
)
from app.questions.generation.models import (
    ExistingQuestionItem,
    GeneratedQuestionItem,
    QuestionGenerationOptions,
)
from app.questions.generation.research_context import build_research_context
from app.services import guest_research_service, guest_service, question_service


class QuestionGenerationResearchMissingError(Exception):
    """Raised when a guest has no completed research to generate from."""


@dataclass
class QuestionGenerationRunResult:
    guest: Guest
    research: GuestResearch
    generation_run_id: uuid.UUID
    generator_provider: str
    generator_model: str | None
    requested_count: int
    candidate_count: int
    generated_count: int
    duplicates_filtered_count: int
    refill_attempts: int
    semantic_pairs_checked: int
    questions: list[GeneratedQuestionItem]


def _existing_question_context(question: Question, index: int) -> ExistingQuestionItem:
    return ExistingQuestionItem(
        id=f"Q{index}",
        text=question.text_,
        topic=question.topic,
        source=question.source,
        intent_summary=question.intent_summary,
        research_item_ids=list(question.research_item_ids or []),
    )


def _generated_as_existing(
    question: GeneratedQuestionItem, index: int
) -> ExistingQuestionItem:
    return ExistingQuestionItem(
        id=f"N{index}",
        text=question.text,
        topic=question.topic,
        source="candidate",
        intent_summary=question.intent_summary,
        research_item_ids=question.research_item_ids,
    )


def _bounded_prompt_history(
    items: list[ExistingQuestionItem], limit: int
) -> list[ExistingQuestionItem]:
    if len(items) <= limit:
        return items
    oldest_count = limit // 2
    return [*items[:oldest_count], *items[-(limit - oldest_count) :]]


class QuestionGenerationEngine:
    """Generate a diversified candidate pool and enforce uniqueness against
    both the current batch and every saved manual/AI question for the guest."""

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
        saved_questions = question_service.get_questions(
            db,
            guest_id,
            limit=settings.question_generation_max_existing_questions,
        )
        existing = [
            _existing_question_context(question, index)
            for index, question in enumerate(saved_questions, 1)
        ]
        existing_for_prompt = _bounded_prompt_history(
            existing, settings.question_generation_max_existing_prompt_questions
        )

        requested_count = options.count
        pool_count = min(
            settings.question_generation_max_candidates,
            max(
                requested_count,
                math.ceil(
                    requested_count
                    * settings.question_generation_candidate_multiplier
                ),
            ),
        )
        pool_options = options.model_copy(update={"count": pool_count})

        raw_candidates: list[GeneratedQuestionItem] = []
        accepted: list[GeneratedQuestionItem] = []
        rejected_count = 0
        semantic_pairs_checked = 0
        refill_attempts = 0

        first = await self._generator.generate(
            guest, research_items, pool_options, existing_for_prompt
        )
        first_candidates = first.questions[:pool_count]
        raw_candidates.extend(first_candidates)
        filtered = await filter_unique_candidates(
            first_candidates,
            existing,
            self._generator,
            lexical_duplicate_threshold=settings.question_generation_lexical_duplicate_threshold,
            intent_duplicate_threshold=settings.question_generation_intent_duplicate_threshold,
            semantic_candidate_threshold=settings.question_generation_semantic_candidate_threshold,
            max_semantic_pairs=settings.question_generation_max_semantic_pairs,
        )
        accepted.extend(filtered.accepted)
        rejected_count += len(filtered.rejected)
        semantic_pairs_checked += filtered.semantic_pairs_checked

        while (
            len(accepted) < requested_count
            and refill_attempts < settings.question_generation_max_refill_attempts
        ):
            refill_attempts += 1
            deficit = requested_count - len(accepted)
            refill_count = min(
                settings.question_generation_max_candidates,
                max(
                    deficit,
                    math.ceil(
                        deficit * settings.question_generation_candidate_multiplier
                    ),
                ),
            )
            refill_options = options.model_copy(update={"count": refill_count})
            avoid = [
                *existing_for_prompt,
                *(
                    _generated_as_existing(question, index)
                    for index, question in enumerate(raw_candidates, 1)
                ),
            ]
            refill = await self._generator.generate(
                guest, research_items, refill_options, avoid
            )
            refill_candidates = refill.questions[:refill_count]
            raw_candidates.extend(refill_candidates)
            comparison_history = [
                *existing,
                *(
                    _generated_as_existing(question, index)
                    for index, question in enumerate(accepted, 1)
                ),
            ]
            refill_filtered = await filter_unique_candidates(
                refill_candidates,
                comparison_history,
                self._generator,
                lexical_duplicate_threshold=settings.question_generation_lexical_duplicate_threshold,
                intent_duplicate_threshold=settings.question_generation_intent_duplicate_threshold,
                semantic_candidate_threshold=settings.question_generation_semantic_candidate_threshold,
                max_semantic_pairs=settings.question_generation_max_semantic_pairs,
            )
            accepted.extend(refill_filtered.accepted)
            rejected_count += len(refill_filtered.rejected)
            semantic_pairs_checked += refill_filtered.semantic_pairs_checked

        questions = select_diverse_questions(accepted, requested_count)
        return QuestionGenerationRunResult(
            guest=guest,
            research=research,
            generation_run_id=uuid.uuid4(),
            generator_provider=self._generator.provider_name,
            generator_model=self._generator.model_name,
            requested_count=requested_count,
            candidate_count=len(raw_candidates),
            generated_count=len(questions),
            duplicates_filtered_count=rejected_count,
            refill_attempts=refill_attempts,
            semantic_pairs_checked=semantic_pairs_checked,
            questions=questions,
        )


def get_question_generation_engine() -> QuestionGenerationEngine:
    from app.questions.generation.factory import build_question_generator

    return QuestionGenerationEngine(generator=build_question_generator())
