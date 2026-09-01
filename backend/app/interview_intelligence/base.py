from abc import ABC, abstractmethod

from app.interview_intelligence.models import QuestionAnswerMatchResult, QuestionContext


class InterviewMatchingError(Exception):
    """Base for all Q&A-matcher-layer failures. A provider-specific matcher
    (e.g. Groq) raises concrete subclasses; the API layer maps them to
    appropriate HTTP status codes without leaking upstream details."""


class InterviewMatcherConfigurationError(InterviewMatchingError):
    """Raised when INTERVIEW_MATCHER_PROVIDER is unset/unsupported, or the
    selected matcher is missing required configuration (e.g. an API key).
    Must never silently fall back - the caller needs to know real matching
    did not run."""


class InterviewMatcherTimeoutError(InterviewMatchingError):
    """Raised when a matcher's upstream call exceeds its timeout."""


class InterviewMatcherValidationError(InterviewMatchingError):
    """Raised when a matcher's structured output fails schema validation."""


class InterviewMatcherTranscriptTooLongError(InterviewMatchingError):
    """Raised when the transcript exceeds
    INTERVIEW_MATCHER_MAX_TRANSCRIPT_CHARS. Deliberately NOT silently
    truncated - see app/interview_intelligence/service.py."""


class QuestionAnswerMatcher(ABC):
    """Vendor-agnostic transcript-to-question matching abstraction. Consumes
    ONLY the transcript text and the saved question list supplied by the
    caller - never performs its own research or browsing."""

    provider_name: str = "unknown"
    model_name: str | None = None

    @abstractmethod
    async def match(
        self, transcript: str, questions: list[QuestionContext]
    ) -> QuestionAnswerMatchResult:
        raise NotImplementedError
