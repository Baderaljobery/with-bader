from app.core.config import settings
from app.questions.improvement.base import QuestionImprover, QuestionImproverConfigurationError
from app.questions.improvement.mock import MockQuestionImprover


def build_question_improver() -> QuestionImprover:
    """Resolve the configured question improver.

    QUESTION_IMPROVER_PROVIDER: "mock" (default) or "groq". An unsupported
    value - or "groq" without GROQ_API_KEY configured - fails clearly rather
    than silently falling back to mock.
    """
    provider = (settings.question_improver_provider or "mock").strip().lower()

    if provider == "mock":
        return MockQuestionImprover()

    if provider == "groq":
        if not settings.groq_api_key:
            raise QuestionImproverConfigurationError(
                "Provider 'groq' requires GROQ_API_KEY, which is not configured"
            )
        from app.questions.improvement.groq import GroqQuestionImprover

        return GroqQuestionImprover(
            api_key=settings.groq_api_key,
            model=settings.groq_question_improvement_model,
            timeout_seconds=settings.groq_timeout_seconds,
        )

    raise QuestionImproverConfigurationError(
        f"Unknown question improver provider '{provider}' (supported: mock, groq)"
    )
