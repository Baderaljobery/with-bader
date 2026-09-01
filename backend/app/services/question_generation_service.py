import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.schemas.question_generation import SelectedGeneratedQuestion
from app.services.guest_service import get_guest_by_id


def save_generated_questions(
    db: Session, guest_id: uuid.UUID, selected: list[SelectedGeneratedQuestion]
) -> list[Question]:
    """Persist selected AI-generated questions into the existing questions
    table, after existing questions, without touching them.

    Provenance (research_item_ids, source_urls, category, priority, reason,
    follow_up_questions) is accepted from the client but NOT yet persisted
    with the row - the existing schema has no columns for it (see the
    generation task's final report). Only text/topic/source/status/position
    are stored.

    No QuestionVersion row is created here, matching the existing
    manual-question convention: question_service.create_question() does not
    auto-create a version either, so this stays consistent rather than
    introducing new behavior.
    """
    get_guest_by_id(db, guest_id)

    next_position = (
        db.scalar(
            select(func.coalesce(func.max(Question.position), -1)).where(
                Question.guest_id == guest_id
            )
        )
        + 1
    )

    created: list[Question] = []
    for offset, item in enumerate(selected):
        question = Question(
            guest_id=guest_id,
            text_=item.text,
            source="ai_generated",
            status="draft",
            topic=item.topic,
            position=next_position + offset,
        )
        db.add(question)
        created.append(question)

    db.commit()
    for question in created:
        db.refresh(question)

    return created
