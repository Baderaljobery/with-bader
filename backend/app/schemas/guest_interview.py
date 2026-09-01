import uuid
from typing import Literal

from pydantic import BaseModel

from app.schemas.guest_transcript import GuestTranscriptResponse

AnswerStatus = Literal["not_answered", "answered", "uncertain"]
AnswerSource = Literal["manual", "ai_extracted"]


class QuestionAnswerStateResponse(BaseModel):
    question_id: uuid.UUID
    question: str
    spoken_question: str | None = None
    answer: str | None = None
    answer_status: AnswerStatus
    answer_source: AnswerSource | None = None
    confidence: float | None = None


class GuestInterviewMatchResponse(BaseModel):
    guest_id: uuid.UUID
    transcript: GuestTranscriptResponse
    questions: list[QuestionAnswerStateResponse]
