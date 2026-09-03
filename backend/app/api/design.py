import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.design_generation.base import (
    ImageGenerationError,
    ImageGeneratorConfigurationError,
    ImageGeneratorTimeoutError,
)
from app.design_generation.engine import (
    SlideImageGenerationEngine,
    SlideImageGenerationError,
    get_slide_image_engine,
)
from app.design_planning.base import (
    SlidePlannerConfigurationError,
    SlidePlannerTimeoutError,
    SlidePlanningError,
)
from app.design_planning.engine import (
    DesignContentPlanner,
    PlanContextInsufficientError,
    get_design_content_planner,
)
from app.design_planning.models import SlidePlanningOptions, SlideRoleSpec
from app.schemas.design_draft import DesignDraftResponse, DesignDraftUpdate
from app.schemas.design_generation import (
    DesignCreateRequest,
    DesignPlanRequest,
    DesignPlanResponse,
    PlannedSlide,
    SlideRegenerateRequest,
)
from app.models.design_draft import DesignDraft
from app.models.design_slide import DesignSlide
from app.schemas.design_slide import DesignSlideResponse, DesignSlideUpdate
from app.services import content_service, design_service, guest_service

router = APIRouter(prefix="/api/guests/{guest_id}/designs", tags=["designs"])
detail_router = APIRouter(prefix="/api/designs", tags=["designs"])


def _resolve_planner() -> DesignContentPlanner:
    try:
        return get_design_content_planner()
    except SlidePlannerConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


def _resolve_image_engine() -> SlideImageGenerationEngine:
    try:
        return get_slide_image_engine()
    except ImageGeneratorConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


def _get_slide_or_404(draft: DesignDraft, slide_index: int) -> DesignSlide:
    for slide in draft.slides:
        if slide.slide_index == slide_index:
            return slide
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Slide {slide_index} not found in design draft '{draft.id}'",
    )


@router.get("", response_model=list[DesignDraftResponse])
def list_designs(guest_id: uuid.UUID, db: Session = Depends(get_db)) -> list[DesignDraftResponse]:
    try:
        return design_service.get_design_drafts(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/plan", response_model=DesignPlanResponse)
async def plan_design(
    guest_id: uuid.UUID,
    request: DesignPlanRequest,
    db: Session = Depends(get_db),
    planner: DesignContentPlanner = Depends(_resolve_planner),
) -> DesignPlanResponse:
    """Step 1 (Part 12): structured text preview only - no image is
    generated and nothing is persisted here. The user reviews/edits this
    before POST {router}/ actually saves a design set."""
    options = SlidePlanningOptions(
        platform=request.platform,
        slide_roles=[SlideRoleSpec(index=item.index, role=item.role) for item in request.slide_roles],
        template_id=request.template_id,
        custom_instructions=request.custom_instructions,
    )
    try:
        result = await planner.plan_slides(
            guest_id, db, request.content_draft_id, request.question_ids, request.notebook_block_ids, options
        )
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except content_service.ContentDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PlanContextInsufficientError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SlidePlannerTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except SlidePlannerConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SlidePlanningError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    sources_used = sorted({item.category for item in result.context_items})
    return DesignPlanResponse(
        guest_id=guest_id,
        template_id=request.template_id,
        slide_count=request.slide_count,
        slides=[
            PlannedSlide(index=s.index, role=s.role, headline=s.headline, body_text=s.body_text, cta_text=s.cta_text)
            for s in result.slides
        ],
        sources_used=sources_used,
        ai_provider=result.planner_provider,
        ai_model=result.planner_model,
    )


@router.post("", response_model=DesignDraftResponse, status_code=status.HTTP_201_CREATED)
def create_design(
    guest_id: uuid.UUID, request: DesignCreateRequest, db: Session = Depends(get_db)
) -> DesignDraftResponse:
    """Step 2 (Part 12): persists the user-approved slide structure. Still
    no images - see POST /api/designs/{design_id}/generate."""
    try:
        return design_service.create_design_draft(db, guest_id, request)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{design_id}", response_model=DesignDraftResponse)
def get_design(design_id: uuid.UUID, db: Session = Depends(get_db)) -> DesignDraftResponse:
    try:
        return design_service.get_design_draft_by_id(db, design_id)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{design_id}", response_model=DesignDraftResponse)
def update_design(
    design_id: uuid.UUID, draft_in: DesignDraftUpdate, db: Session = Depends(get_db)
) -> DesignDraftResponse:
    try:
        return design_service.update_design_draft(db, design_id, draft_in)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_design(design_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        design_service.delete_design_draft(db, design_id)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


async def _generate_images(
    design_id: uuid.UUID, db: Session, engine: SlideImageGenerationEngine, *, all_slides: bool
) -> DesignDraftResponse:
    try:
        draft = design_service.get_design_draft_by_id(db, design_id)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    try:
        if all_slides:
            return await design_service.regenerate_all_slide_images(db, draft, engine)
        return await design_service.generate_missing_slide_images(db, draft, engine)
    except ImageGeneratorTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except ImageGeneratorConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SlideImageGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except ImageGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@detail_router.post("/{design_id}/generate", response_model=DesignDraftResponse)
async def generate_design_images(
    design_id: uuid.UUID,
    db: Session = Depends(get_db),
    engine: SlideImageGenerationEngine = Depends(_resolve_image_engine),
) -> DesignDraftResponse:
    """Generates images ONLY for slides that don't have one yet (Part 28:
    cost control - never regenerates an existing image as a side effect)."""
    return await _generate_images(design_id, db, engine, all_slides=False)


@detail_router.post("/{design_id}/regenerate-all", response_model=DesignDraftResponse)
async def regenerate_all_design_images(
    design_id: uuid.UUID,
    db: Session = Depends(get_db),
    engine: SlideImageGenerationEngine = Depends(_resolve_image_engine),
) -> DesignDraftResponse:
    """Explicit "regenerate every slide" (Part 26) - always triggers
    slide_count paid model calls; the frontend must confirm with the user
    before calling this."""
    return await _generate_images(design_id, db, engine, all_slides=True)


@detail_router.post("/{design_id}/slides/{slide_index}/regenerate", response_model=DesignSlideResponse)
async def regenerate_slide_image(
    design_id: uuid.UUID,
    slide_index: int,
    request: SlideRegenerateRequest,
    db: Session = Depends(get_db),
    engine: SlideImageGenerationEngine = Depends(_resolve_image_engine),
) -> DesignSlideResponse:
    """Regenerates ONE slide's image only (Part 25) - preserves that
    slide's own text, every other slide, and the shared configuration."""
    try:
        draft = design_service.get_design_draft_by_id(db, design_id)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    slide = _get_slide_or_404(draft, slide_index)

    try:
        return await design_service.regenerate_one_slide_image(
            db, draft, slide, engine, request.custom_instructions
        )
    except ImageGeneratorTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except ImageGeneratorConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SlideImageGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except ImageGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@detail_router.patch("/{design_id}/slides/{slide_index}", response_model=DesignSlideResponse)
def update_slide(
    design_id: uuid.UUID, slide_index: int, update: DesignSlideUpdate, db: Session = Depends(get_db)
) -> DesignSlideResponse:
    try:
        return design_service.update_slide_text(db, design_id, slide_index, update)
    except (design_service.DesignDraftNotFoundError, design_service.DesignSlideNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
