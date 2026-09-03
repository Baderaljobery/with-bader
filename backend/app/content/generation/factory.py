from app.content.generation.base import ContentGenerator, ContentGeneratorConfigurationError
from app.content.generation.mock import MockContentGenerator
from app.core.config import settings


def build_content_generator() -> ContentGenerator:
    """Resolve the configured content generator.

    CONTENT_GENERATOR_PROVIDER: "mock" (default) or "groq". An unsupported
    value - or "groq" without GROQ_API_KEY configured - fails clearly rather
    than silently falling back to mock, matching how the question generator
    factory handles the same situation.
    """
    provider = (settings.content_generator_provider or "mock").strip().lower()

    if provider == "mock":
        return MockContentGenerator()

    if provider == "groq":
        if not settings.groq_api_key:
            raise ContentGeneratorConfigurationError(
                "Provider 'groq' requires GROQ_API_KEY, which is not configured"
            )
        from app.content.generation.groq import GroqContentGenerator

        return GroqContentGenerator(
            api_key=settings.groq_api_key,
            model=settings.groq_content_model,
            timeout_seconds=settings.groq_timeout_seconds,
            max_output_tokens=settings.groq_max_output_tokens,
        )

    raise ContentGeneratorConfigurationError(
        f"Unknown content generator provider '{provider}' (supported: mock, groq)"
    )
