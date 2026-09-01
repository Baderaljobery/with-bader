from abc import ABC, abstractmethod

from app.models.question import Question
from app.questions.improvement.models import (
    QuestionImprovementContext,
    QuestionImprovementOptions,
    QuestionImprovementResult,
)


class QuestionImprovementError(Exception):
    """Base for all question-improvement-layer failures. A provider-specific
    improver (e.g. Groq) raises concrete subclasses; the API layer maps them
    to appropriate HTTP status codes without leaking upstream details."""


class QuestionImproverConfigurationError(QuestionImprovementError):
    """Raised when QUESTION_IMPROVER_PROVIDER is unset/unsupported, or the
    selected improver is missing required configuration (e.g. an API key).
    Must never silently fall back - the caller needs to know real
    improvement did not run."""


class QuestionImproverTimeoutError(QuestionImprovementError):
    """Raised when an improver's upstream call exceeds its timeout."""


class QuestionImproverValidationError(QuestionImprovementError):
    """Raised when an improver's structured output fails schema validation."""


class QuestionImprover(ABC):
    """Vendor-agnostic question-improvement abstraction. Rewrites the wording
    of ONE existing question using only its own text and (optionally) guest
    metadata/research highlights already on file - never performs its own
    research (no browsing, no Exa/Tavily calls)."""

    provider_name: str = "unknown"
    model_name: str | None = None

    @abstractmethod
    async def improve(
        self,
        question: Question,
        options: QuestionImprovementOptions,
        context: QuestionImprovementContext | None = None,
    ) -> QuestionImprovementResult:
        raise NotImplementedError
