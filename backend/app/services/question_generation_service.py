import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.guest import Guest
from app.models.guest_research import GuestResearch
from app.models.question import Question
from app.questions.generation.research_context import build_research_context
from app.questions.generation.models import ResearchContextItem
from app.questions.generation.similarity import (
    lexical_similarity,
    normalize_question_text,
    normalized_question_hash,
    same_optional_label,
)
from app.schemas.question_generation import (
    SelectedGeneratedQuestion,
    SkippedGeneratedQuestion,
)
from app.services.guest_service import get_guest_by_id


class QuestionGenerationResearchMismatchError(Exception):
    pass


@dataclass
class GeneratedQuestionSaveResult:
    created: list[Question]
    skipped: list[SkippedGeneratedQuestion]


def _semantic_match(item: SelectedGeneratedQuestion, existing: Question) -> bool:
    text_score = lexical_similarity(item.text, existing.text_)
    if item.intent_summary and existing.intent_summary:
        if normalize_question_text(item.intent_summary) == normalize_question_text(
            existing.intent_summary
        ):
            return True
        intent_score = lexical_similarity(item.intent_summary, existing.intent_summary)
        return intent_score >= settings.question_generation_intent_duplicate_threshold and (
            same_optional_label(item.topic, existing.topic)
            or text_score
            >= settings.question_generation_lexical_duplicate_threshold * 0.65
        )
    return text_score >= settings.question_generation_lexical_duplicate_threshold


def _find_duplicate(
    item: SelectedGeneratedQuestion, existing: list[Question]
) -> tuple[str, Question] | None:
    normalized = normalize_question_text(item.text)
    for question in existing:
        if item.candidate_id and question.generation_candidate_id == item.candidate_id:
            return "already_saved", question
        if normalize_question_text(question.text_) == normalized:
            return "exact_duplicate", question
        if _semantic_match(item, question):
            return "semantic_duplicate", question
    return None


def _trusted_research_context(
    db: Session,
    guest_id: uuid.UUID,
    research_id: uuid.UUID | None,
) -> tuple[dict[str, ResearchContextItem], int | None]:
    if research_id is None:
        return {}, None
    research = db.get(GuestResearch, research_id)
    if research is None or research.guest_id != guest_id:
        raise QuestionGenerationResearchMismatchError(
            "The generated-question research does not belong to this guest"
        )
    return (
        {context.id: context for context in build_research_context(research)},
        research.version,
    )


def _trusted_research_metadata(
    indexed: dict[str, ResearchContextItem], item: SelectedGeneratedQuestion
) -> tuple[list[str], list[str]]:
    valid_ids: list[str] = []
    urls: list[str] = []
    seen_urls: set[str] = set()
    for research_item_id in item.research_item_ids:
        context = indexed.get(research_item_id)
        if context is None:
            continue
        valid_ids.append(research_item_id)
        for url in context.source_urls:
            if url not in seen_urls:
                urls.append(url)
                seen_urls.add(url)
    return valid_ids, urls


def save_generated_questions(
    db: Session,
    guest_id: uuid.UUID,
    selected: list[SelectedGeneratedQuestion],
    *,
    generation_run_id: uuid.UUID | None = None,
    research_id: uuid.UUID | None = None,
    research_version: int | None = None,
) -> GeneratedQuestionSaveResult:
    """Persist selected candidates with final exact/intent/idempotency checks."""
    get_guest_by_id(db, guest_id)
    db.scalar(select(Guest.id).where(Guest.id == guest_id).with_for_update())

    existing = list(
        db.scalars(
            select(Question)
            .where(Question.guest_id == guest_id)
            .order_by(Question.position, Question.created_at, Question.id)
        ).all()
    )
    indexed_research, actual_research_version = _trusted_research_context(
        db, guest_id, research_id
    )
    if (
        research_version is not None
        and actual_research_version is not None
        and research_version != actual_research_version
    ):
        raise QuestionGenerationResearchMismatchError(
            "The generated-question research version does not match the selected research"
        )
    next_position = (
        db.scalar(
            select(func.coalesce(func.max(Question.position), -1)).where(
                Question.guest_id == guest_id
            )
        )
        + 1
    )

    created: list[Question] = []
    skipped: list[SkippedGeneratedQuestion] = []
    for item in selected:
        duplicate = _find_duplicate(item, existing)
        if duplicate is not None:
            reason, question = duplicate
            skipped.append(
                SkippedGeneratedQuestion(
                    candidate_id=item.candidate_id,
                    text=item.text,
                    reason=reason,
                    duplicate_of_question_id=question.id,
                )
            )
            continue

        valid_ids, source_urls = _trusted_research_metadata(indexed_research, item)
        question = Question(
            guest_id=guest_id,
            text_=item.text.strip(),
            source="ai_generated",
            status="draft",
            topic=item.topic,
            category=item.category,
            priority=item.priority,
            intent_summary=(item.intent_summary or "").strip() or None,
            position=next_position + len(created),
            research_id=research_id,
            research_version=actual_research_version,
            research_item_ids=valid_ids,
            source_urls=source_urls,
            follow_up_questions=list(item.follow_up_questions),
            generation_reason=item.reason,
            generation_run_id=generation_run_id,
            generation_candidate_id=item.candidate_id,
            ai_normalized_text_hash=normalized_question_hash(item.text),
        )
        try:
            with db.begin_nested():
                db.add(question)
                db.flush()
        except IntegrityError:
            clauses = [Question.guest_id == guest_id]
            if item.candidate_id:
                clauses.append(Question.generation_candidate_id == item.candidate_id)
            else:
                clauses.append(
                    Question.ai_normalized_text_hash
                    == normalized_question_hash(item.text)
                )
            duplicate_row = db.scalar(select(Question).where(*clauses))
            skipped.append(
                SkippedGeneratedQuestion(
                    candidate_id=item.candidate_id,
                    text=item.text,
                    reason="concurrent_duplicate",
                    duplicate_of_question_id=(duplicate_row.id if duplicate_row else None),
                )
            )
            continue

        created.append(question)
        existing.append(question)

    db.commit()
    for question in created:
        db.refresh(question)
    return GeneratedQuestionSaveResult(created=created, skipped=skipped)
