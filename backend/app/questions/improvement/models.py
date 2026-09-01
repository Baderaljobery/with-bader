from pydantic import BaseModel, Field


class QuestionImprovementOptions(BaseModel):
    language: str = "ar"
    style: str = "conversational"
    goal: str = "clarity"


class QuestionImprovementContext(BaseModel):
    """Optional, lightweight context - guest metadata + a few research
    highlights - used only so the model doesn't accidentally contradict
    known facts. Never triggers new research; loaded only if it already
    exists (see app/api/question_improvement.py)."""

    guest_name: str | None = None
    guest_job_title: str | None = None
    guest_company: str | None = None
    research_highlights: list[str] = Field(default_factory=list)


class QuestionImprovementResult(BaseModel):
    original_text: str
    improved_text: str
    reason: str | None = None
    changes: list[str] = Field(default_factory=list)
