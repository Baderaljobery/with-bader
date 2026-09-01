from app.core.config import settings
from app.questions.generation.base import QuestionGenerator, QuestionGeneratorConfigurationError
from app.questions.generation.mock import MockQuestionGenerator


def build_question_generator() -> QuestionGenerator:
    """Resolve the configured question generator.

    QUESTION_GENERATOR_PROVIDER: "mock" (default) or "groq". An unsupported
    value - or "groq" without GROQ_API_KEY configured - fails clearly rather
    than silently falling back to mock, matching how the research extractor
    factory handles the same situation.
    """
    provider = (settings.question_generator_provider or "mock").strip().lower()

    if provider == "mock":
        return MockQuestionGenerator()

    if provider == "groq":
        if not settings.groq_api_key:
            raise QuestionGeneratorConfigurationError(
                "Provider 'groq' requires GROQ_API_KEY, which is not configured"
            )
        from app.questions.generation.groq import GroqQuestionGenerator

        return GroqQuestionGenerator(
            api_key=settings.groq_api_key,
            model=settings.groq_question_model,
            timeout_seconds=settings.groq_timeout_seconds,
            max_output_tokens=settings.groq_max_output_tokens,
        )

    raise QuestionGeneratorConfigurationError(
        f"Unknown question generator provider '{provider}' (supported: mock, groq)"
    )
