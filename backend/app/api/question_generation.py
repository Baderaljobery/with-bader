import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.questions.generation.base import (
    QuestionGenerationError,
    QuestionGeneratorConfigurationError,
    QuestionGeneratorTimeoutError,
)
from app.questions.generation.engine import (
    QuestionGenerationEngine,
    QuestionGenerationResearchMissingError,
    get_question_generation_engine,
)
from app.questions.generation.models import QuestionGenerationOptions
from app.schemas.question import QuestionResponse
from app.schemas.question_generation import (
    GeneratedQuestionResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    QuestionGenerationSaveRequest,
    QuestionGenerationSaveResponse,
)
from app.services import guest_service
from app.services.question_generation_service import save_generated_questions

router = APIRouter(prefix="/api/guests/{guest_id}/questions", tags=["question-generation"])


def _resolve_engine() -> QuestionGenerationEngine:
    """FastAPI-aware wrapper around get_question_generation_engine().

    A misconfigured generator (e.g. QUESTION_GENERATOR_PROVIDER=groq without
    GROQ_API_KEY) must fail clearly rather than silently falling back to the
    mock, so this converts that into a clean 500 before it ever reaches the
    endpoint body.
    """
    try:
        return get_question_generation_engine()
    except QuestionGeneratorConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.post("/generate", response_model=QuestionGenerationResponse)
async def generate_questions(
    guest_id: uuid.UUID,
    request: QuestionGenerationRequest,
    db: Session = Depends(get_db),
    engine: QuestionGenerationEngine = Depends(_resolve_engine),
    current_user: User = Depends(get_current_user),
) -> QuestionGenerationResponse:
    """Preview only - does NOT persist anything. Use /generated/save to
    store the questions the user selects from this preview."""
    options = QuestionGenerationOptions(
        count=request.count,
        language=request.language,
        style=request.style,
        include_followups=request.include_followups,
        topics=request.topics,
    )
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        result = await engine.generate_questions(guest_id, db, options)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except QuestionGenerationResearchMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except QuestionGeneratorTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except QuestionGeneratorConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except QuestionGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return QuestionGenerationResponse(
        guest_id=guest_id,
        research_id=result.research.id,
        research_version=result.research.version,
        generator_provider=result.generator_provider,
        generator_model=result.generator_model,
        requested_count=result.requested_count,
        generated_count=result.generated_count,
        questions=[
            GeneratedQuestionResponse(
                text=q.text,
                topic=q.topic,
                category=q.category,
                priority=q.priority,
                research_item_ids=q.research_item_ids,
                source_urls=q.source_urls,
                reason=q.reason,
                follow_up_questions=q.follow_up_questions,
            )
            for q in result.questions
        ],
    )


@router.post(
    "/generated/save",
    response_model=QuestionGenerationSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_generated(
    guest_id: uuid.UUID,
    request: QuestionGenerationSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionGenerationSaveResponse:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        created = save_generated_questions(db, guest_id, request.questions)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return QuestionGenerationSaveResponse(
        guest_id=guest_id,
        saved_count=len(created),
        questions=[QuestionResponse.model_validate(q) for q in created],
    )
