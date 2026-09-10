from abc import ABC, abstractmethod

from app.models.guest import Guest
from app.questions.generation.models import (
    ExistingQuestionItem,
    QuestionGenerationOptions,
    QuestionGenerationResult,
    ResearchContextItem,
    SemanticComparisonDecision,
    SemanticComparisonPair,
)


class QuestionGenerationError(Exception):
    """Base for all question-generator-layer failures. A provider-specific
    generator (e.g. Groq) raises concrete subclasses; the API layer maps
    them to appropriate HTTP status codes without leaking upstream details."""


class QuestionGeneratorConfigurationError(QuestionGenerationError):
    """Raised when QUESTION_GENERATOR_PROVIDER is unset/unsupported, or the
    selected generator is missing required configuration (e.g. an API key).
    Must never silently fall back - the caller needs to know real
    generation did not run."""


class QuestionGeneratorTimeoutError(QuestionGenerationError):
    """Raised when a generator's upstream call exceeds its timeout."""


class QuestionGeneratorValidationError(QuestionGenerationError):
    """Raised when a generator's structured output fails schema/Pydantic
    validation and cannot be trusted enough to return."""


class QuestionGenerator(ABC):
    """Vendor-agnostic question-generation abstraction. Consumes only the
    guest metadata and a compact, already-source-grounded research context -
    it must never perform its own research (no browsing, no search calls)."""

    provider_name: str = "unknown"
    model_name: str | None = None

    @abstractmethod
    async def generate(
        self,
        guest: Guest,
        research_items: list[ResearchContextItem],
        options: QuestionGenerationOptions,
        existing_questions: list[ExistingQuestionItem] | None = None,
    ) -> QuestionGenerationResult:
        raise NotImplementedError

    async def classify_duplicate_pairs(
        self, pairs: list[SemanticComparisonPair]
    ) -> list[SemanticComparisonDecision]:
        """Optional bounded semantic layer. Non-AI/test generators safely
        fall back to the deterministic exact/lexical/intent checks."""
        return []
