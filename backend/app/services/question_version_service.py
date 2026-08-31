import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.question_version import QuestionVersion
from app.schemas.question_version import QuestionVersionCreate
from app.services.question_service import get_question_by_id


class QuestionVersionNotFoundError(Exception):
    """Raised when a question version does not exist."""


def create_question_version(
    db: Session, question_id: uuid.UUID, version_in: QuestionVersionCreate
) -> QuestionVersion:
    get_question_by_id(db, question_id)

    highest_version = db.scalar(
        select(func.coalesce(func.max(QuestionVersion.version), 0)).where(
            QuestionVersion.question_id == question_id
        )
    )

    version = QuestionVersion(
        question_id=question_id,
        version=highest_version + 1,
        text_=version_in.text,
        source=version_in.source,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def get_question_versions(db: Session, question_id: uuid.UUID) -> list[QuestionVersion]:
    get_question_by_id(db, question_id)

    stmt = (
        select(QuestionVersion)
        .where(QuestionVersion.question_id == question_id)
        .order_by(QuestionVersion.version.asc())
    )
    return list(db.scalars(stmt).all())


def get_question_version_by_id(db: Session, version_id: uuid.UUID) -> QuestionVersion:
    version = db.get(QuestionVersion, version_id)
    if version is None:
        raise QuestionVersionNotFoundError(f"Question version '{version_id}' not found")
    return version
