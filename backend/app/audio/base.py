from abc import ABC, abstractmethod

from app.audio.models import AudioInput, TranscriptionOptions, TranscriptionResult


class SpeechToTextError(Exception):
    """Base for all STT-layer failures. A provider-specific implementation
    (e.g. Groq) raises concrete subclasses; the API layer maps them to
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


class FFmpegNotAvailableError(STTProviderConfigurationError):
    """Raised only when a file exceeds stt_direct_max_bytes (so it needs
    chunking - see app/audio/chunking.py) and ffmpeg is not installed/on
    PATH on this server. Files at or under the direct limit never need
    ffmpeg and are unaffected. A subclass of STTProviderConfigurationError
    so existing callers' exception handling (-> 500) needs no changes."""


class AudioProcessingError(STTValidationError):
    """Raised when ffmpeg itself fails while normalizing or splitting an
    uploaded file - e.g. the file is corrupted or not real audio despite
    passing the extension/content-type check. A subclass of
    STTValidationError so existing callers' exception handling (-> 422)
    needs no changes."""


class SpeechToTextProvider(ABC):
    """Vendor-agnostic speech-to-text abstraction. Application code depends
    only on this + the models in app/audio/models.py - never on a concrete
    provider's SDK types. This is what made swapping Cohere for Groq
    Whisper (2026-09-06) a config change plus one new provider file, not a
    rewrite of every caller - and what makes the next swap the same."""

    provider_name: str = "unknown"
    model_name: str = "unknown"

    @abstractmethod
    async def transcribe(
        self, audio: AudioInput, options: TranscriptionOptions | None = None
    ) -> TranscriptionResult:
        raise NotImplementedError
