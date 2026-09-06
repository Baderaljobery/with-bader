from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    text: str
    provider: str
    model: str
    language: str | None = None
    duration_seconds: float | None = None
    # Non-breaking additions (Groq Whisper migration, 2026-09-06): only
    # present/true when the upload exceeded the direct-upload limit and was
    # automatically split into sequential parts - see
    # app/audio/service.py's _transcribe_chunked. Existing consumers that
    # only read `text` are unaffected.
    chunked: bool = False
    chunk_count: int | None = None
