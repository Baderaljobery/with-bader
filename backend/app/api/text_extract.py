from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

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
from app.core.auth import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.transcription import TranscriptionResponse

router = APIRouter(prefix="/api/text-extract", tags=["text-extract"])


def _resolve_service() -> SpeechToTextService:
    """FastAPI-aware wrapper around get_speech_to_text_service().

    A misconfigured provider (e.g. STT_PROVIDER=groq without
    GROQ_API_KEY) must fail clearly rather than silently doing nothing.
    """
    try:
        return get_speech_to_text_service()
    except STTProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.post("/audio", response_model=TranscriptionResponse)
async def extract_text_from_audio(
    file: UploadFile = File(...),
    service: SpeechToTextService = Depends(_resolve_service),
    current_user: User = Depends(get_current_user),
) -> TranscriptionResponse:
    """Stateless utility: audio in, text out. Defaults to Arabic (see
    GroqWhisperSTTProvider / GROQ_STT_LANGUAGE) - the caller does not
    choose a language.

    No guest_id, no Guest/Question/Interview created, no transcript
    persisted anywhere - the returned response is the only thing that
    outlives this request. Audio at or under stt_direct_max_bytes is held
    in memory only and never written to disk; a larger file is briefly
    written to a unique temp directory for ffmpeg chunking and always
    deleted before this call returns (see app/audio/service.py) - no audio
    is ever kept afterward either way.
    """
    try:
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

        result = await service.transcribe(audio)
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
    finally:
        # Guarantees any internally-spooled temp data backing this upload is
        # discarded, whether transcription succeeded, failed, timed out, or
        # validation rejected the file first.
        await file.close()

    metadata = result.metadata or {}
    return TranscriptionResponse(
        text=result.text,
        provider=result.provider,
        model=result.model,
        language=result.language,
        duration_seconds=result.duration_seconds,
        chunked=bool(metadata.get("chunked", False)),
        chunk_count=metadata.get("chunk_count"),
    )
