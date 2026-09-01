from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    text: str
    provider: str
    model: str
    language: str | None = None
    duration_seconds: float | None = None
