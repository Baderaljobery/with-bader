from app.core.config import settings
from app.research.extraction.base import ResearchExtractor, ResearchExtractorConfigurationError
from app.research.extraction.mock import MockResearchExtractor


def build_research_extractor() -> ResearchExtractor:
    """Resolve the configured extractor.

    RESEARCH_EXTRACTOR_PROVIDER: "mock" (default) or "groq". An unsupported
    value - or "groq" without GROQ_API_KEY configured - fails clearly rather
    than silently falling back to mock, matching how an unsupported/
    misconfigured search provider is handled.
    """
    provider = (settings.research_extractor_provider or "mock").strip().lower()

    if provider == "mock":
        return MockResearchExtractor()

    if provider == "groq":
        if not settings.groq_api_key:
            raise ResearchExtractorConfigurationError(
                "Provider 'groq' requires GROQ_API_KEY, which is not configured"
            )
        from app.research.extraction.groq import GroqResearchExtractor

        return GroqResearchExtractor(
            api_key=settings.groq_api_key,
            model=settings.groq_research_model,
            timeout_seconds=settings.groq_timeout_seconds,
            max_output_tokens=settings.groq_max_output_tokens,
            reasoning_effort=settings.groq_reasoning_effort,
            max_sources=settings.research_extractor_max_sources,
            max_source_chars=settings.research_extractor_max_source_chars,
        )

    raise ResearchExtractorConfigurationError(
        f"Unknown extractor provider '{provider}' (supported: mock, groq)"
    )
