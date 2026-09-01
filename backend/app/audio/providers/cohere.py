import logging

import cohere
import cohere.core
import httpx

from app.audio.base import STTProviderError, STTTimeoutError, SpeechToTextProvider
from app.audio.models import AudioInput, TranscriptionOptions, TranscriptionResult

logger = logging.getLogger(__name__)


class CohereSTTProvider(SpeechToTextProvider):
    """Speech-to-text via Cohere's Audio Transcription API.

    Cohere-specific types/errors never leave this module - the rest of the
    application only ever sees AudioInput/TranscriptionOptions/
    TranscriptionResult (app/audio/models.py) and the generic STT*
    exceptions (app/audio/base.py). This isolation is what lets a future
    provider (Deepgram, AssemblyAI, ...) replace this file alone.
    """

    provider_name = "cohere"

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 60.0) -> None:
        self._client = cohere.AsyncClient(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model

    async def transcribe(
        self, audio: AudioInput, options: TranscriptionOptions | None = None
    ) -> TranscriptionResult:
        # With Bader's Cohere STT is Arabic-only for now - this is a
        # Cohere-provider-specific decision, so it's hard-coded here rather
        # than deferred to the caller. options.language is intentionally
        # ignored: the generic TranscriptionOptions.language field stays in
        # the domain model for future providers/models that do support
        # configurable language, but Cohere doesn't use it today.
        try:
            response = await self._client.audio.transcriptions.create(
                model=self._model,
                language="ar",
                file=(audio.filename, audio.content, audio.content_type),
            )
        except httpx.TimeoutException as exc:
            logger.info(
                "cohere stt timeout provider=%s model=%s filename=%s size_bytes=%d",
                self.provider_name,
                self._model,
                audio.filename,
                audio.size_bytes,
            )
            raise STTTimeoutError("Cohere transcription request timed out") from exc
        except cohere.GatewayTimeoutError as exc:
            raise STTTimeoutError("Cohere transcription request timed out") from exc
        except cohere.core.ApiError as exc:
            logger.info(
                "cohere stt api_error provider=%s model=%s status=%s",
                self.provider_name,
                self._model,
                exc.status_code,
            )
            raise STTProviderError(
                f"Cohere transcription failed with status {exc.status_code or 'unknown'}"
            ) from exc
        except httpx.HTTPError as exc:
            raise STTProviderError(
                f"Cohere transcription request failed: {exc.__class__.__name__}"
            ) from exc

        text = (response.text or "").strip()

        logger.info(
            "cohere stt success provider=%s model=%s filename=%s size_bytes=%d text_length=%d",
            self.provider_name,
            self._model,
            audio.filename,
            audio.size_bytes,
            len(text),
        )

        # Cohere's response model currently exposes only `text`. language is
        # "ar" here because the application knows the request explicitly
        # asked for Arabic - not because Cohere echoed it back. duration/
        # segments stay None until a provider actually returns them.
        return TranscriptionResult(
            text=text,
            language="ar",
            duration_seconds=None,
            provider=self.provider_name,
            model=self._model,
            segments=None,
            metadata=None,
        )
