import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content_draft import ContentDraft
from app.schemas.content_draft import ContentDraftCreate, ContentDraftUpdate
from app.services.guest_service import get_guest_by_id


class ContentDraftNotFoundError(Exception):
    """Raised when a content draft does not exist."""


def create_content_draft(
    db: Session, guest_id: uuid.UUID, draft_in: ContentDraftCreate
) -> ContentDraft:
    get_guest_by_id(db, guest_id)

    draft = ContentDraft(guest_id=guest_id, **draft_in.model_dump())
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def get_content_drafts(db: Session, guest_id: uuid.UUID) -> list[ContentDraft]:
    get_guest_by_id(db, guest_id)

    stmt = (
        select(ContentDraft)
        .where(ContentDraft.guest_id == guest_id)
        .order_by(ContentDraft.updated_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_content_draft_by_id(db: Session, content_id: uuid.UUID) -> ContentDraft:
    draft = db.get(ContentDraft, content_id)
    if draft is None:
        raise ContentDraftNotFoundError(f"Content draft '{content_id}' not found")
    return draft


def update_content_draft(
    db: Session, content_id: uuid.UUID, draft_in: ContentDraftUpdate
) -> ContentDraft:
    draft = get_content_draft_by_id(db, content_id)

    for field, value in draft_in.model_dump(exclude_unset=True).items():
        setattr(draft, field, value)

    db.commit()
    db.refresh(draft)
    return draft


def delete_content_draft(db: Session, content_id: uuid.UUID) -> None:
    draft = get_content_draft_by_id(db, content_id)
    db.delete(draft)
    db.commit()


def approve_content_draft(db: Session, content_id: uuid.UUID) -> ContentDraft:
    """Marks a draft approved - Arabic UI label "اعتماد المحتوى". Approval is
    a local status flip only; it never triggers any external action (no
    Design Engine call, no publishing) - see app/api/content.py."""
    draft = get_content_draft_by_id(db, content_id)
    draft.status = "approved"
    db.commit()
    db.refresh(draft)
    return draft
