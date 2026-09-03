from app.core.config import settings
from app.design_generation.base import ImageGenerator, ImageGeneratorConfigurationError


def build_image_generator() -> ImageGenerator:
    """OpenRouter is the only image-generation provider for this phase - no
    provider-selection env var, no mock/fallback in the production path (see
    ImageGenerator in base.py). Fails clearly if OPENROUTER_API_KEY is
    missing rather than silently doing nothing."""
    if not settings.openrouter_api_key:
        raise ImageGeneratorConfigurationError(
            "Design image generation requires OPENROUTER_API_KEY, which is not configured"
        )

    from app.design_generation.openrouter import OpenRouterImageGenerator

    return OpenRouterImageGenerator(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_image_model,
        timeout_seconds=settings.openrouter_timeout_seconds,
    )
