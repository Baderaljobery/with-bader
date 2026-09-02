import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.audio.base import (
    STTFileTooLargeError,
    STTProviderConfigurationError,
    STTProviderError,
    STTTimeoutError,
    STTUnsupportedFormatError,
    STTValidationError,
)
from app.audio.models import AudioInput
from app.audio.service import SpeechToTextService, get_speech_to_text_service
from app.audio.validation import (
    read_bounded_upload,
    validate_file_size,
    validate_filename_and_content_type,
)
from app.core.config import settings
from app.database.session import get_db
from app.interview_intelligence.base import (
    InterviewMatcherConfigurationError,
    InterviewMatcherTimeoutError,
    InterviewMatcherTranscriptTooLongError,
    InterviewMatchingError,
)
from app.interview_intelligence.service import (
    InterviewIntelligenceService,
    QuestionMatchOutcome,
    get_interview_intelligence_service,
)
from app.schemas.guest_interview import GuestInterviewMatchResponse, QuestionAnswerStateResponse
from app.schemas.guest_transcript import (
    GuestTranscriptCreate,
    GuestTranscriptResponse,
    GuestTranscriptTextUpdate,
)
from app.services import guest_service, guest_transcript_service
from app.services.guest_transcript_service import (
    GuestTranscriptAlreadyExistsError,
    GuestTranscriptNotFoundError,
)

router = APIRouter(prefix="/api/guests/{guest_id}", tags=["guest-interview"])


def _resolve_stt_service() -> SpeechToTextService:
    try:
        return get_speech_to_text_service()
    except STTProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


def _resolve_matcher_service() -> InterviewIntelligenceService:
    try:
        return get_interview_intelligence_service()
    except InterviewMatcherConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


def _outcomes_to_response(
    outcomes: list[QuestionMatchOutcome],
) -> list[QuestionAnswerStateResponse]:
    return [
        QuestionAnswerStateResponse(
            question_id=outcome.question.id,
            question=outcome.question.text_,
            spoken_question=outcome.spoken_question,
            answer=outcome.answer,
            answer_status=outcome.answer_status,
            answer_source=outcome.answer_source,
            confidence=outcome.confidence,
        )
        for outcome in outcomes
    ]


def _raise_for_matcher_error(exc: Exception) -> None:
    if isinstance(exc, InterviewMatcherTranscriptTooLongError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if isinstance(exc, InterviewMatcherTimeoutError):
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    if isinstance(exc, InterviewMatcherConfigurationError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if isinstance(exc, InterviewMatchingError):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/transcribe-interview",
    response_model=GuestInterviewMatchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def transcribe_interview(
    guest_id: uuid.UUID,
    file: UploadFile = File(...),
    replace_existing: bool = Query(default=False),
    db: Session = Depends(get_db),
    stt_service: SpeechToTextService = Depends(_resolve_stt_service),
    matcher_service: InterviewIntelligenceService = Depends(_resolve_matcher_service),
) -> GuestInterviewMatchResponse:
    """Audio -> SpeechToTextService -> transcript saved -> answer matching.

    Reuses the exact same SpeechToTextService as General Text Extract - no
    duplicated transcription code. Audio is discarded after processing,
    exactly as in Text Extract; only the resulting transcript text and
    question answers are ever persisted.
    """
    try:
        guest_service.get_guest_by_id(db, guest_id)

        validate_filename_and_content_type(file.filename, file.content_type)
        max_bytes = settings.stt_max_file_size_mb * 1024 * 1024
        content = await read_bounded_upload(file, max_bytes)
        validate_file_size(len(content))

        audio = AudioInput(
            filename=file.filename or "audio",
            content_type=file.content_type,
            content=content,
            size_bytes=len(content),
        )
        transcription = await stt_service.transcribe(audio)

        transcript = guest_transcript_service.create_guest_transcript(
            db,
            guest_id,
            GuestTranscriptCreate(
                text=transcription.text,
                stt_provider=transcription.provider,
                stt_model=transcription.model,
            ),
            replace_existing=replace_existing,
        )

        outcomes = await matcher_service.match_and_apply(db, guest_id, transcript.text_)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except STTUnsupportedFormatError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)
        ) from exc
    except STTFileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)
        ) from exc
    except STTValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except STTTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except STTProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except STTProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except GuestTranscriptAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InterviewMatchingError as exc:
        _raise_for_matcher_error(exc)
        raise
    finally:
        # Guarantees any internally-spooled temp data backing this upload is
        # discarded, whether transcription/matching succeeded, failed, timed
        # out, or validation rejected the file first. No audio is retained.
        await file.close()

    return GuestInterviewMatchResponse(
        guest_id=guest_id,
        matcher_provider=matcher_service.matcher_provider,
        matcher_model=matcher_service.matcher_model,
        transcript=GuestTranscriptResponse.model_validate(transcript),
        questions=_outcomes_to_response(outcomes),
    )


@router.get("/transcript", response_model=GuestTranscriptResponse)
def get_transcript(guest_id: uuid.UUID, db: Session = Depends(get_db)) -> GuestTranscriptResponse:
    try:
        transcript = guest_transcript_service.get_guest_transcript_or_raise(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GuestTranscriptNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return GuestTranscriptResponse.model_validate(transcript)


@router.patch("/transcript", response_model=GuestTranscriptResponse)
def update_transcript(
    guest_id: uuid.UUID, request: GuestTranscriptTextUpdate, db: Session = Depends(get_db)
) -> GuestTranscriptResponse:
    """Manual correction only - deliberately does NOT automatically re-run
    answer matching. Call POST /match-answers explicitly afterward."""
    try:
        transcript = guest_transcript_service.update_guest_transcript_text(
            db, guest_id, request.text
        )
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GuestTranscriptNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return GuestTranscriptResponse.model_validate(transcript)


@router.post("/match-answers", response_model=GuestInterviewMatchResponse)
async def match_answers(
    guest_id: uuid.UUID,
    db: Session = Depends(get_db),
    matcher_service: InterviewIntelligenceService = Depends(_resolve_matcher_service),
) -> GuestInterviewMatchResponse:
    """Re-run matching against the currently saved transcript + current
    question list, without re-uploading audio. Manual answers are never
    overwritten; ai_extracted answers may be refreshed."""
    try:
        transcript = guest_transcript_service.get_guest_transcript_or_raise(db, guest_id)
        outcomes = await matcher_service.match_and_apply(db, guest_id, transcript.text_)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GuestTranscriptNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InterviewMatchingError as exc:
        _raise_for_matcher_error(exc)
        raise

    return GuestInterviewMatchResponse(
        guest_id=guest_id,
        matcher_provider=matcher_service.matcher_provider,
        matcher_model=matcher_service.matcher_model,
        transcript=GuestTranscriptResponse.model_validate(transcript),
        questions=_outcomes_to_response(outcomes),
    )
