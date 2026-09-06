import logging

from groq import APIConnectionError, APIError, APITimeoutError, AsyncGroq

from app.audio.base import STTProviderError, STTTimeoutError, SpeechToTextProvider
from app.audio.models import AudioInput, TranscriptionOptions, TranscriptionResult

logger = logging.getLogger(__name__)


class GroqWhisperSTTProvider(SpeechToTextProvider):
    """Speech-to-text via Groq's hosted Whisper endpoint
    (api.groq.com/openai/v1/audio/transcriptions, OpenAI-compatible shape).

    Groq-specific types/errors never leave this module - the rest of the
    application only ever sees AudioInput/TranscriptionOptions/
    TranscriptionResult (app/audio/models.py) and the generic STT*
    exceptions (app/audio/base.py). Same isolation the Cohere provider it
    replaces had - this is what makes the swap a config change at the
    factory, not a rewrite of every caller.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 60.0,
        default_language: str = "ar",
    ) -> None:
        self._client = AsyncGroq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model
        self._default_language = default_language

    async def transcribe(
        self, audio: AudioInput, options: TranscriptionOptions | None = None
    ) -> TranscriptionResult:
        # Always sends an explicit language - never left to Whisper's
        # auto-detection - defaulting to the app-wide configured language
        # (Arabic) unless a caller's options explicitly ask for another one.
        language = (options.language if options and options.language else None) or self._default_language

        try:
            response = await self._client.audio.transcriptions.create(
                model=self._model,
                file=(audio.filename, audio.content, audio.content_type or "application/octet-stream"),
                language=language,
                response_format="json",
                temperature=0,
            )
        except APITimeoutError as exc:
            logger.info(
                "groq stt timeout provider=%s model=%s filename=%s size_bytes=%d",
                self.provider_name,
                self._model,
                audio.filename,
                audio.size_bytes,
            )
            raise STTTimeoutError("Groq transcription request timed out") from exc
        except APIConnectionError as exc:
            raise STTProviderError(
                f"Groq transcription request failed: {exc.__class__.__name__}"
            ) from exc
        except APIError as exc:
            status_code = getattr(exc, "status_code", "unknown")
            logger.info(
                "groq stt api_error provider=%s model=%s status=%s",
                self.provider_name,
                self._model,
                status_code,
            )
            raise STTProviderError(f"Groq transcription failed with status {status_code}") from exc

        text = (response.text or "").strip()

        logger.info(
            "groq stt success provider=%s model=%s filename=%s size_bytes=%d text_length=%d",
            self.provider_name,
            self._model,
            audio.filename,
            audio.size_bytes,
            len(text),
        )

        # Groq's "json" response_format exposes only `text` (the richer
        # `verbose_json` format also returns per-segment timestamps, but
        # nothing today needs them - see app/audio/models.py's
        # TranscriptionSegment for how a future caller could opt into that
        # without any contract change). duration stays None for the same
        # reason Cohere's provider left it None: never guessed, only ever
        # populated when a provider actually returns it.
        return TranscriptionResult(
            text=text,
            language=language,
            duration_seconds=None,
            provider=self.provider_name,
            model=self._model,
            segments=None,
            metadata=None,
        )
