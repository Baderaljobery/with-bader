from abc import ABC, abstractmethod

from app.design_generation.models import ImageGenerationResult, SlideImageOptions


class ImageGenerationError(Exception):
    """Base for all image-generator-layer failures. A provider-specific
    generator (e.g. Gemini) raises concrete subclasses; the API layer maps
    them to appropriate HTTP status codes without leaking upstream details."""


class ImageGeneratorConfigurationError(ImageGenerationError):
    """Raised when the selected image generator is missing required
    configuration (e.g. GEMINI_API_KEY). Must never silently fall back - the
    caller needs to know real generation did not run."""


class ImageGeneratorTimeoutError(ImageGenerationError):
    """Raised when a generator's upstream call exceeds its timeout."""


class ImageGeneratorValidationError(ImageGenerationError):
    """Raised when a generator responds without a usable generated image."""


class ImageGenerator(ABC):
    """Vendor-agnostic image-generation abstraction. Only one concrete
    implementation exists today (OpenRouter, see openrouter.py) - this ABC
    exists so a second provider can be added later without reshaping the
    engine/API layer, not because a second provider is planned now."""

    provider_name: str = "unknown"
    model_name: str | None = None

    @abstractmethod
    async def generate(self, prompt: str, options: SlideImageOptions) -> ImageGenerationResult:
        raise NotImplementedError
