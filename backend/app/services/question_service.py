import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate
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
) -> list[Question]:
    get_guest_by_id(db, guest_id)

    stmt = select(Question).where(Question.guest_id == guest_id)
    if status is not None:
        stmt = stmt.where(Question.status == status)
    if source is not None:
        stmt = stmt.where(Question.source == source)
    if topic is not None:
        stmt = stmt.where(Question.topic == topic)
    stmt = stmt.order_by(Question.position.asc())

    return list(db.scalars(stmt).all())


def get_question_by_id(db: Session, question_id: uuid.UUID) -> Question:
    question = db.get(Question, question_id)
    if question is None:
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
