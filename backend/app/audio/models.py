from typing import Any

from pydantic import BaseModel, Field


class AudioInput(BaseModel):
    """In-memory audio payload. Never written to disk by this application -
    the bytes exist only for the duration of one request."""

    filename: str
    content_type: str | None = None
    content: bytes
    size_bytes: int


class TranscriptionOptions(BaseModel):
    language: str | None = None
    prompt: str | None = None


class TranscriptionSegment(BaseModel):
    """Reserved for future providers that support diarization/timestamps
    (e.g. Deepgram, AssemblyAI). Never fabricated - only populated when a
    provider actually returns this data."""

    start: float | None = None
    end: float | None = None
    text: str
    speaker: str | None = None


class TranscriptionResult(BaseModel):
    """The ONLY shape any application code should depend on. A provider
    that returns richer data (segments, duration, detected language) may
    populate those fields; a provider that doesn't (like Groq's default
    "json" response_format today) leaves them None - never guessed or
    invented."""

    text: str
    language: str | None = None
    duration_seconds: float | None = None
    provider: str
    model: str
    segments: list[TranscriptionSegment] | None = None
    metadata: dict[str, Any] | None = None
