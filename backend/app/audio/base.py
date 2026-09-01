from abc import ABC, abstractmethod

from app.audio.models import AudioInput, TranscriptionOptions, TranscriptionResult


class SpeechToTextError(Exception):
    """Base for all STT-layer failures. A provider-specific implementation
    (e.g. Cohere) raises concrete subclasses; the API layer maps them to
    appropriate HTTP status codes without leaking upstream details."""


class STTProviderConfigurationError(SpeechToTextError):
    """Raised when STT_PROVIDER is unset/unsupported, or the selected
    provider is missing required configuration (e.g. an API key). Must
    never silently fall back - the caller needs to know transcription did
    not run."""


class STTTimeoutError(SpeechToTextError):
    """Raised when a provider's upstream call exceeds its timeout."""


class STTProviderError(SpeechToTextError):
    """Raised when a provider's upstream API call fails (network/HTTP/API)."""


class STTValidationError(SpeechToTextError):
    """Raised when the uploaded audio itself is invalid (e.g. empty)."""


class STTUnsupportedFormatError(STTValidationError):
    """Raised when the uploaded file's extension/content-type isn't allowed."""


class STTFileTooLargeError(STTValidationError):
    """Raised when the uploaded file exceeds the configured size limit."""


class SpeechToTextProvider(ABC):
    """Vendor-agnostic speech-to-text abstraction. Application code depends
    only on this + the models in app/audio/models.py - never on a concrete
    provider's SDK types. This is what makes swapping Cohere for another
    provider later a config change, not a code change."""

    provider_name: str = "unknown"
    model_name: str = "unknown"

    @abstractmethod
    async def transcribe(
        self, audio: AudioInput, options: TranscriptionOptions | None = None
    ) -> TranscriptionResult:
        raise NotImplementedError
