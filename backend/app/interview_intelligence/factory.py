from app.core.config import settings
from app.interview_intelligence.base import (
    InterviewMatcherConfigurationError,
    QuestionAnswerMatcher,
)
from app.interview_intelligence.mock import MockQuestionAnswerMatcher


def build_question_answer_matcher() -> QuestionAnswerMatcher:
    """Resolve the configured Q&A matcher.

    INTERVIEW_MATCHER_PROVIDER: "mock" (default) or "groq". An unsupported
    value - or "groq" without GROQ_API_KEY configured - fails clearly
    rather than silently falling back to mock.
    """
    provider = (settings.interview_matcher_provider or "mock").strip().lower()

    if provider == "mock":
        return MockQuestionAnswerMatcher()

    if provider == "groq":
        if not settings.groq_api_key:
            raise InterviewMatcherConfigurationError(
                "Provider 'groq' requires GROQ_API_KEY, which is not configured"
            )
        from app.interview_intelligence.groq import GroqQuestionAnswerMatcher

        return GroqQuestionAnswerMatcher(
            api_key=settings.groq_api_key,
            model=settings.groq_interview_matcher_model,
            timeout_seconds=settings.groq_timeout_seconds,
            max_output_tokens=settings.groq_max_output_tokens,
        )

    raise InterviewMatcherConfigurationError(
        f"Unknown interview matcher provider '{provider}' (supported: mock, groq)"
    )
