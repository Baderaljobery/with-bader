import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
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
from app.models.user import User
from app.schemas.design_draft import DesignDraftResponse, DesignDraftUpdate
from app.schemas.design_generation import (
    DesignCreateRequest,
    DesignPlanRequest,
    DesignPlanResponse,
    PlannedSlide,
)
from app.schemas.design_slide import DesignSlideResponse, DesignSlideUpdate
from app.services import content_service, design_service, guest_service

router = APIRouter(prefix="/api/guests/{guest_id}/designs", tags=["designs"])
detail_router = APIRouter(prefix="/api/designs", tags=["designs"])


def _resolve_planner() -> DesignContentPlanner:
    try:
        return get_design_content_planner()
    except SlidePlannerConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("", response_model=list[DesignDraftResponse])
def list_designs(
    guest_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DesignDraftResponse]:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return design_service.get_design_drafts(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/plan", response_model=DesignPlanResponse)
async def plan_design(
    guest_id: uuid.UUID,
    request: DesignPlanRequest,
    db: Session = Depends(get_db),
    planner: DesignContentPlanner = Depends(_resolve_planner),
    current_user: User = Depends(get_current_user),
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
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
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
    guest_id: uuid.UUID,
    request: DesignCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DesignDraftResponse:
    """Step 2 (Part 12): persists the user-approved slide structure. The
    strict template-renderer flow never generates or stores an AI image for
    any slide - rendering happens entirely client-side."""
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return design_service.create_design_draft(db, guest_id, request)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{design_id}", response_model=DesignDraftResponse)
def get_design(
    design_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DesignDraftResponse:
    try:
        return design_service.get_design_draft_by_id_for_user(db, design_id, current_user.id)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{design_id}", response_model=DesignDraftResponse)
def update_design(
    design_id: uuid.UUID,
    draft_in: DesignDraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DesignDraftResponse:
    try:
        design_service.get_design_draft_by_id_for_user(db, design_id, current_user.id)
        return design_service.update_design_draft(db, design_id, draft_in)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_design(
    design_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        design_service.get_design_draft_by_id_for_user(db, design_id, current_user.id)
        design_service.delete_design_draft(db, design_id)
    except design_service.DesignDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{design_id}/slides/{slide_index}", response_model=DesignSlideResponse)
def update_slide(
    design_id: uuid.UUID,
    slide_index: int,
    update: DesignSlideUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DesignSlideResponse:
    try:
        design_service.get_design_draft_by_id_for_user(db, design_id, current_user.id)
        return design_service.update_slide_text(db, design_id, slide_index, update)
    except (design_service.DesignDraftNotFoundError, design_service.DesignSlideNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
