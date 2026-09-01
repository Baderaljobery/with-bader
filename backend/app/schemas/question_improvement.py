import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator

QuestionImprovementLanguage = Literal["ar", "en"]
QuestionImprovementStyle = Literal["conversational", "professional", "deep", "concise"]
QuestionImprovementGoal = Literal["clarity", "depth", "brevity", "natural"]


class QuestionImprovementRequest(BaseModel):
    language: QuestionImprovementLanguage = "ar"
    style: QuestionImprovementStyle = "conversational"
    goal: QuestionImprovementGoal = "clarity"


class QuestionImprovementPreviewResponse(BaseModel):
    question_id: uuid.UUID
    original_text: str
    improved_text: str
    reason: str | None = None
    changes: list[str] = Field(default_factory=list)


class QuestionImprovementAcceptRequest(BaseModel):
    improved_text: str = Field(min_length=1, max_length=1000)

    @field_validator("improved_text")
    @classmethod
    def _strip_and_require_non_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("improved_text must not be blank")
        return stripped
