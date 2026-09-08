import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.design_generation.storage import delete_generated_image
from app.models.design_draft import DesignDraft
from app.models.design_slide import DesignSlide
from app.schemas.design_draft import DesignDraftUpdate
from app.schemas.design_generation import DesignCreateRequest
from app.schemas.design_slide import DesignSlideUpdate
from app.services.guest_service import get_guest_by_id


class DesignDraftNotFoundError(Exception):
    """Raised when a design draft does not exist."""


class DesignSlideNotFoundError(Exception):
    """Raised when a design slide does not exist within a given draft."""


def get_design_drafts(
    db: Session, guest_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[DesignDraft]:
    get_guest_by_id(db, guest_id)

    stmt = (
        select(DesignDraft)
        .options(selectinload(DesignDraft.slides))
        .where(DesignDraft.guest_id == guest_id)
        .order_by(DesignDraft.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_design_draft_by_id(db: Session, design_id: uuid.UUID) -> DesignDraft:
    stmt = (
        select(DesignDraft).options(selectinload(DesignDraft.slides)).where(DesignDraft.id == design_id)
    )
    draft = db.scalars(stmt).first()
    if draft is None:
        raise DesignDraftNotFoundError(f"Design draft '{design_id}' not found")
    return draft


def get_design_draft_by_id_for_user(db: Session, design_id: uuid.UUID, user_id: uuid.UUID) -> DesignDraft:
    draft = get_design_draft_by_id(db, design_id)
    if draft.guest.created_by != user_id:
        raise DesignDraftNotFoundError(f"Design draft '{design_id}' not found")
    return draft


def get_design_slide(db: Session, design_id: uuid.UUID, slide_index: int) -> DesignSlide:
    draft = get_design_draft_by_id(db, design_id)
    for slide in draft.slides:
        if slide.slide_index == slide_index:
            return slide
    raise DesignSlideNotFoundError(f"Slide {slide_index} not found in design draft '{design_id}'")


def create_design_draft(db: Session, guest_id: uuid.UUID, request: DesignCreateRequest) -> DesignDraft:
    """Persists the user-approved slide structure - the strict template-
    renderer flow never generates or stores an AI image for any slide."""
    get_guest_by_id(db, guest_id)

    draft = DesignDraft(
        guest_id=guest_id,
        content_draft_id=request.content_draft_id,
        title=request.title,
        platform=request.platform,
        template_id=request.template_id,
        slide_count=request.slide_count,
        aspect_ratio=request.aspect_ratio,
        background_color=request.background_color,
        accent_color=request.accent_color,
        customizations={
            "question_ids": [str(qid) for qid in request.question_ids],
            "notebook_block_ids": [str(bid) for bid in request.notebook_block_ids],
            "custom_instructions": request.custom_instructions,
        },
    )
    draft.slides = [
        DesignSlide(
            slide_index=slide.index,
            role=slide.role,
            headline=slide.headline,
            body_text=slide.body_text,
            cta_text=slide.cta_text,
        )
        for slide in sorted(request.slides, key=lambda s: s.index)
    ]

    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def update_design_draft(db: Session, design_id: uuid.UUID, draft_in: DesignDraftUpdate) -> DesignDraft:
    draft = get_design_draft_by_id(db, design_id)

    for field, value in draft_in.model_dump(exclude_unset=True).items():
        setattr(draft, field, value)

    db.commit()
    db.refresh(draft)
    return draft


def update_slide_text(
    db: Session, design_id: uuid.UUID, slide_index: int, update: DesignSlideUpdate
) -> DesignSlide:
    slide = get_design_slide(db, design_id, slide_index)

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(slide, field, value)

    db.commit()
    db.refresh(slide)
    return slide


def delete_design_draft(db: Session, design_id: uuid.UUID) -> None:
    draft = get_design_draft_by_id(db, design_id)
    # Best-effort cleanup for any slide carrying image-generation metadata
    # from before the Design Engine became a strict deterministic-template
    # renderer (see app/design_generation/storage.py) - a no-op for every
    # slide created by the current flow, which never sets image_path.
    for slide in draft.slides:
        delete_generated_image(slide.image_path)
    db.delete(draft)
    db.commit()
