import uuid

from sqlalchemy.orm import Session

from app.models.question import Question
from app.schemas.question_version import QuestionVersionCreate
from app.services.question_service import get_question_by_id
from app.services.question_version_service import create_question_version


class QuestionImprovementNoChangeError(Exception):
    """Raised when the improved text is identical to the question's current
    text - accepting it would create a no-op duplicate version."""


def accept_question_improvement(
    db: Session, question_id: uuid.UUID, improved_text: str
) -> Question:
    """Preserve the current question text as a historical QuestionVersion,
    record the new improved text as another QuestionVersion (source=
    "ai_improved"), then update the live question row. Never silently
    overwrites the original - both the pre- and post-improvement text remain
    recoverable via question_versions.
    """
    question = get_question_by_id(db, question_id)

    current_text = question.text_.strip()
    improved_text = improved_text.strip()

    if improved_text == current_text:
        raise QuestionImprovementNoChangeError(
            f"Question '{question_id}' improved_text is identical to its current text"
        )

    # Preserve the current (pre-improvement) text under its own origin
    # (manual stays manual, ai_generated stays ai_generated in history).
    create_question_version(
        db, question_id, QuestionVersionCreate(text=current_text, source=question.source)
    )
    # Record the new improved text as its own historical version too.
    create_question_version(
        db, question_id, QuestionVersionCreate(text=improved_text, source="ai_improved")
    )

    question.text_ = improved_text
    question.source = "ai_improved"
    db.commit()
    db.refresh(question)

    return question
