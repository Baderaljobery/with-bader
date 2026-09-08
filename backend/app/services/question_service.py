import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.schemas.question import QuestionAnswerUpdate, QuestionCreate, QuestionUpdate
from app.services.guest_service import get_guest_by_id


class QuestionNotFoundError(Exception):
    """Raised when a question does not exist."""


def create_question(db: Session, guest_id: uuid.UUID, question_in: QuestionCreate) -> Question:
    get_guest_by_id(db, guest_id)

    data = question_in.model_dump()
    data["text_"] = data.pop("text")

    question = Question(guest_id=guest_id, **data)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_questions(
    db: Session,
    guest_id: uuid.UUID,
    status: str | None = None,
    source: str | None = None,
    topic: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Question]:
    get_guest_by_id(db, guest_id)

    stmt = select(Question).where(Question.guest_id == guest_id)
    if status is not None:
        stmt = stmt.where(Question.status == status)
    if source is not None:
        stmt = stmt.where(Question.source == source)
    if topic is not None:
        stmt = stmt.where(Question.topic == topic)
    # Stable tie-breakers are required because new questions default to the
    # same position; AI matching assigns Q1/Q2 refs from this ordering.
    stmt = (
        stmt.order_by(Question.position.asc(), Question.created_at.asc(), Question.id.asc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())


def get_question_by_id(db: Session, question_id: uuid.UUID) -> Question:
    question = db.get(Question, question_id)
    if question is None:
        raise QuestionNotFoundError(f"Question '{question_id}' not found")
    return question


def get_question_by_id_for_user(db: Session, question_id: uuid.UUID, user_id: uuid.UUID) -> Question:
    """Ownership check for the direct /api/questions/{question_id} routes -
    see guest_service.get_guest_by_id_for_user for the same pattern."""
    question = get_question_by_id(db, question_id)
    if question.guest.created_by != user_id:
        raise QuestionNotFoundError(f"Question '{question_id}' not found")
    return question


def update_question(db: Session, question_id: uuid.UUID, question_in: QuestionUpdate) -> Question:
    question = get_question_by_id(db, question_id)

    updates = question_in.model_dump(exclude_unset=True)
    if "text" in updates:
        updates["text_"] = updates.pop("text")

    for field, value in updates.items():
        setattr(question, field, value)

    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question_id: uuid.UUID) -> None:
    question = get_question_by_id(db, question_id)
    db.delete(question)
    db.commit()


def set_question_answer(
    db: Session, question_id: uuid.UUID, answer_in: QuestionAnswerUpdate
) -> Question:
    """Manual answer entry/edit/clear - independent of AI, always wins.

    A non-empty answer marks the question answered/manual. A null or blank
    answer clears it back to not_answered with no source. spoken_question is
    only touched if the caller actually included that key in the request.
    """
    question = get_question_by_id(db, question_id)
    updates = answer_in.model_dump(exclude_unset=True)

    if "spoken_question" in updates:
        question.spoken_question = updates["spoken_question"]

    answer_text = (updates.get("answer") or "").strip() or None
    if answer_text:
        question.answer = answer_text
        question.answer_status = "answered"
        question.answer_source = "manual"
    else:
        question.answer = None
        question.answer_status = "not_answered"
        question.answer_source = None

    question.answer_updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(question)
    return question


def apply_answer_match(
    question: Question,
    *,
    answer: str | None,
    answer_status: str,
    answer_source: str | None,
    spoken_question: str | None = None,
) -> Question:
    """Low-level field setter used by InterviewIntelligenceService.

    Does NOT enforce the manual-answer-protection rule itself - the caller
    (app/interview_intelligence/service.py) decides whether this should be
    called at all for a given question. This only writes what it's told and
    stamps answer_updated_at. No db.commit() here - callers batch-commit.
    """
    question.answer = answer
    question.answer_status = answer_status
    question.answer_source = answer_source
    if spoken_question is not None:
        question.spoken_question = spoken_question
    question.answer_updated_at = datetime.now(timezone.utc)
    return question
