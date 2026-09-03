from app.core.config import settings
from app.design_planning.base import SlidePlanner, SlidePlannerConfigurationError
from app.design_planning.mock import MockSlidePlanner


def build_slide_planner() -> SlidePlanner:
    """Resolve the configured slide planner. SLIDE_PLANNER_PROVIDER: "mock"
    (default) or "groq". An unsupported value - or "groq" without
    GROQ_API_KEY configured - fails clearly rather than silently falling
    back to mock, matching every other provider factory in this project."""
    provider = (settings.slide_planner_provider or "mock").strip().lower()

    if provider == "mock":
        return MockSlidePlanner()

    if provider == "groq":
        if not settings.groq_api_key:
            raise SlidePlannerConfigurationError(
                "Provider 'groq' requires GROQ_API_KEY, which is not configured"
            )
        from app.design_planning.groq import GroqSlidePlanner

        return GroqSlidePlanner(
            api_key=settings.groq_api_key,
            model=settings.groq_slide_planner_model,
            timeout_seconds=settings.groq_timeout_seconds,
            max_output_tokens=settings.groq_max_output_tokens,
        )

    raise SlidePlannerConfigurationError(
        f"Unknown slide planner provider '{provider}' (supported: mock, groq)"
    )
