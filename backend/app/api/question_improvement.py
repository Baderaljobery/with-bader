import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.questions.improvement.base import (
    QuestionImprovementError,
    QuestionImprover,
    QuestionImproverConfigurationError,
    QuestionImproverTimeoutError,
)
from app.questions.improvement.factory import build_question_improver
from app.questions.improvement.models import QuestionImprovementContext, QuestionImprovementOptions
from app.schemas.question import QuestionResponse
from app.schemas.question_improvement import (
    QuestionImprovementAcceptRequest,
    QuestionImprovementPreviewResponse,
    QuestionImprovementRequest,
)
from app.services import guest_research_service, guest_service, question_service
from app.services.question_improvement_service import (
    QuestionImprovementNoChangeError,
    accept_question_improvement,
)

router = APIRouter(prefix="/api/questions/{question_id}", tags=["question-improvement"])


def _resolve_improver() -> QuestionImprover:
    """FastAPI-aware wrapper around build_question_improver().

    A misconfigured improver (e.g. QUESTION_IMPROVER_PROVIDER=groq without
    GROQ_API_KEY) must fail clearly rather than silently falling back to the
    mock, so this converts that into a clean 500 before it ever reaches the
    endpoint body.
    """
    try:
        return build_question_improver()
    except QuestionImproverConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


def _build_lightweight_context(
    db: Session, guest_id: uuid.UUID
) -> QuestionImprovementContext | None:
    """Optional context, loaded only if it already exists - never triggers
    research, never calls Exa/Tavily. Improvement still works with None."""
    try:
        guest = guest_service.get_guest_by_id(db, guest_id)
    except guest_service.GuestNotFoundError:
        return None

    research_highlights: list[str] = []
    research = guest_research_service.get_latest_guest_research(db, guest_id)
    if research is not None:
        for item in (research.achievements or [])[:3]:
            if isinstance(item, dict) and item.get("title"):
                research_highlights.append(item["title"])
        for item in (research.career_history or [])[:3]:
            if isinstance(item, dict) and (item.get("role") or item.get("company")):
                highlight = f"{item.get('role') or ''} at {item.get('company') or ''}".strip()
                if highlight and highlight != "at":
                    research_highlights.append(highlight)

    return QuestionImprovementContext(
        guest_name=guest.name,
        guest_job_title=guest.job_title,
        guest_company=guest.company,
        research_highlights=research_highlights[:5],
    )


@router.post("/improve", response_model=QuestionImprovementPreviewResponse)
async def improve_question(
    question_id: uuid.UUID,
    request: QuestionImprovementRequest = Body(default_factory=QuestionImprovementRequest),
    db: Session = Depends(get_db),
    improver: QuestionImprover = Depends(_resolve_improver),
) -> QuestionImprovementPreviewResponse:
    """Preview only - never modifies the question or creates a QuestionVersion.
    Use /improve/accept to apply the (possibly edited) improved text."""
    try:
        question = question_service.get_question_by_id(db, question_id)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    options = QuestionImprovementOptions(
        language=request.language, style=request.style, goal=request.goal
    )
    context = _build_lightweight_context(db, question.guest_id)

    try:
        result = await improver.improve(question, options, context)
    except QuestionImproverTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except QuestionImproverConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except QuestionImprovementError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return QuestionImprovementPreviewResponse(
        question_id=question_id,
        original_text=result.original_text,
        improved_text=result.improved_text,
        reason=result.reason,
        changes=result.changes,
    )


@router.post("/improve/accept", response_model=QuestionResponse)
def accept_improvement(
    question_id: uuid.UUID,
    request: QuestionImprovementAcceptRequest,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    try:
        return accept_question_improvement(db, question_id, request.improved_text)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except QuestionImprovementNoChangeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
