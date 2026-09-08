import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.content.generation.base import (
    ContentGenerationError,
    ContentGeneratorConfigurationError,
    ContentGeneratorTimeoutError,
)
from app.content.generation.engine import (
    ContentContextInsufficientError,
    ContentGenerationEngine,
    get_content_generation_engine,
)
from app.content.generation.models import ContentGenerationOptions
from app.core.auth import get_current_user
from app.core.pagination import PaginationParams
from app.core.rate_limit import enforce_ai_rate_limit
from app.database.session import get_db
from app.models.user import User
from app.schemas.content_draft import ContentDraftCreate, ContentDraftResponse, ContentDraftUpdate
from app.schemas.content_generation import ContentGenerationRequest, ContentGenerationResponse
from app.services import content_service, guest_service

router = APIRouter(prefix="/api/guests/{guest_id}/content", tags=["content"])
detail_router = APIRouter(prefix="/api/content", tags=["content"])


def _resolve_engine() -> ContentGenerationEngine:
    """FastAPI-aware wrapper around get_content_generation_engine().

    A misconfigured generator (e.g. CONTENT_GENERATOR_PROVIDER=groq without
    GROQ_API_KEY) must fail clearly rather than silently falling back to the
    mock, so this converts that into a clean 500 before it ever reaches the
    endpoint body.
    """
    try:
        return get_content_generation_engine()
    except ContentGeneratorConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    guest_id: uuid.UUID,
    request: ContentGenerationRequest,
    db: Session = Depends(get_db),
    engine: ContentGenerationEngine = Depends(_resolve_engine),
    current_user: User = Depends(enforce_ai_rate_limit),
) -> ContentGenerationResponse:
    """Preview only - does NOT persist anything. Use POST
    /api/guests/{guest_id}/content to save the draft the user reviews from
    this preview."""
    options = ContentGenerationOptions(
        platform=request.platform,
        length=request.length,
        language=request.language,
        custom_instructions=request.custom_instructions,
    )
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        result = await engine.generate_content(guest_id, db, options)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ContentContextInsufficientError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ContentGeneratorTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except ContentGeneratorConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except ContentGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    sources_used = sorted({item.category for item in result.context_items})

    return ContentGenerationResponse(
        guest_id=guest_id,
        platform=request.platform,
        length=request.length,
        language=request.language,
        title=result.title,
        content=result.content,
        sources_used=sources_used,
        ai_provider=result.generator_provider,
        ai_model=result.generator_model,
    )


@router.post("", response_model=ContentDraftResponse, status_code=status.HTTP_201_CREATED)
def create_content(
    guest_id: uuid.UUID,
    draft_in: ContentDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContentDraftResponse:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return content_service.create_content_draft(db, guest_id, draft_in)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[ContentDraftResponse])
def list_content(
    guest_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContentDraftResponse]:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return content_service.get_content_drafts(
            db, guest_id, skip=pagination.skip, limit=pagination.limit
        )
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{content_id}", response_model=ContentDraftResponse)
def get_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContentDraftResponse:
    try:
        return content_service.get_content_draft_by_id_for_user(db, content_id, current_user.id)
    except content_service.ContentDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{content_id}", response_model=ContentDraftResponse)
def update_content(
    content_id: uuid.UUID,
    draft_in: ContentDraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContentDraftResponse:
    try:
        content_service.get_content_draft_by_id_for_user(db, content_id, current_user.id)
        return content_service.update_content_draft(db, content_id, draft_in)
    except content_service.ContentDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        content_service.get_content_draft_by_id_for_user(db, content_id, current_user.id)
        content_service.delete_content_draft(db, content_id)
    except content_service.ContentDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.post("/{content_id}/approve", response_model=ContentDraftResponse)
def approve_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContentDraftResponse:
    """No publishing/handoff side effect - purely a local status flip so
    Design (a future phase) can later filter on approved content."""
    try:
        content_service.get_content_draft_by_id_for_user(db, content_id, current_user.id)
        return content_service.approve_content_draft(db, content_id)
    except content_service.ContentDraftNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
