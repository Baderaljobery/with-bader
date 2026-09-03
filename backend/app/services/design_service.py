import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.design_generation.engine import SlideImageGenerationEngine, SlideImageRequest
from app.design_generation.storage import delete_generated_image, save_generated_image
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


def get_design_drafts(db: Session, guest_id: uuid.UUID) -> list[DesignDraft]:
    get_guest_by_id(db, guest_id)

    stmt = (
        select(DesignDraft)
        .options(selectinload(DesignDraft.slides))
        .where(DesignDraft.guest_id == guest_id)
        .order_by(DesignDraft.updated_at.desc())
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


def get_design_slide(db: Session, design_id: uuid.UUID, slide_index: int) -> DesignSlide:
    draft = get_design_draft_by_id(db, design_id)
    for slide in draft.slides:
        if slide.slide_index == slide_index:
            return slide
    raise DesignSlideNotFoundError(f"Slide {slide_index} not found in design draft '{design_id}'")


def create_design_draft(db: Session, guest_id: uuid.UUID, request: DesignCreateRequest) -> DesignDraft:
    """Persists the user-approved slide structure (Part 12: preview-first -
    no image has been generated for any slide yet, see
    generate_missing_slide_images below)."""
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
    for slide in draft.slides:
        delete_generated_image(slide.image_path)
    db.delete(draft)
    db.commit()


def _build_slide_image_request(draft: DesignDraft, slide: DesignSlide) -> SlideImageRequest:
    custom_instructions = (draft.customizations or {}).get("custom_instructions")
    return SlideImageRequest(
        guest=draft.guest,
        template_id=draft.template_id,
        role=slide.role,
        headline=slide.headline,
        body_text=slide.body_text,
        platform=draft.platform,
        aspect_ratio=draft.aspect_ratio,
        background_color=draft.background_color,
        accent_color=draft.accent_color,
        custom_instructions=custom_instructions,
    )


async def _generate_and_save_slide_image(
    db: Session, draft: DesignDraft, slide: DesignSlide, engine: SlideImageGenerationEngine
) -> DesignSlide:
    old_image_path = slide.image_path
    request = _build_slide_image_request(draft, slide)
    result = await engine.generate_slide_image(request)

    slide.image_path = save_generated_image(result.image_bytes, result.mime_type)
    slide.prompt = result.prompt
    draft.ai_provider = result.generator_provider
    draft.ai_model = result.generator_model

    db.commit()
    db.refresh(slide)

    if old_image_path:
        delete_generated_image(old_image_path)
    return slide


async def generate_missing_slide_images(
    db: Session, draft: DesignDraft, engine: SlideImageGenerationEngine
) -> DesignDraft:
    """Generates images only for slides that don't have one yet - the
    normal first-time flow right after create_design_draft. Cost control
    (Part 28): each slide missing an image is exactly one paid model call,
    slides that already have an image are left untouched."""
    for slide in sorted(draft.slides, key=lambda s: s.slide_index):
        if slide.image_path is None:
            await _generate_and_save_slide_image(db, draft, slide, engine)
    db.refresh(draft)
    return draft


async def regenerate_all_slide_images(
    db: Session, draft: DesignDraft, engine: SlideImageGenerationEngine
) -> DesignDraft:
    """Explicit "regenerate every slide" action (Part 26) - the frontend is
    responsible for confirming this with the user first, since it always
    triggers slide_count paid model calls regardless of what already
    exists."""
    for slide in sorted(draft.slides, key=lambda s: s.slide_index):
        await _generate_and_save_slide_image(db, draft, slide, engine)
    db.refresh(draft)
    return draft


async def regenerate_one_slide_image(
    db: Session,
    draft: DesignDraft,
    slide: DesignSlide,
    engine: SlideImageGenerationEngine,
    custom_instructions_override: str | None,
) -> DesignSlide:
    """Regenerates ONE slide's image only - preserves that slide's own
    (possibly manually-edited) text, every other slide, the template, and
    the design's colors (Part 25). custom_instructions_override applies
    only to this one call, not persisted onto the draft's shared
    customizations."""
    old_image_path = slide.image_path
    request = _build_slide_image_request(draft, slide)
    if custom_instructions_override is not None:
        request.custom_instructions = custom_instructions_override

    result = await engine.generate_slide_image(request)

    slide.image_path = save_generated_image(result.image_bytes, result.mime_type)
    slide.prompt = result.prompt
    draft.ai_provider = result.generator_provider
    draft.ai_model = result.generator_model

    db.commit()
    db.refresh(slide)

    if old_image_path:
        delete_generated_image(old_image_path)
    return slide
