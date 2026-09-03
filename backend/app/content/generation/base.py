from abc import ABC, abstractmethod

from app.content.generation.models import (
    ContentContextItem,
    ContentGenerationOptions,
    ContentGenerationResult,
)
from app.models.guest import Guest


class ContentGenerationError(Exception):
    """Base for all content-generator-layer failures. A provider-specific
    generator (e.g. Groq) raises concrete subclasses; the API layer maps
    them to appropriate HTTP status codes without leaking upstream details."""


class ContentGeneratorConfigurationError(ContentGenerationError):
    """Raised when CONTENT_GENERATOR_PROVIDER is unset/unsupported, or the
    selected generator is missing required configuration (e.g. an API key).
    Must never silently fall back - the caller needs to know real
    generation did not run."""


class ContentGeneratorTimeoutError(ContentGenerationError):
    """Raised when a generator's upstream call exceeds its timeout."""


class ContentGeneratorValidationError(ContentGenerationError):
    """Raised when a generator's structured output fails schema/Pydantic
    validation and cannot be trusted enough to return."""


class ContentGenerator(ABC):
    """Vendor-agnostic content-generation abstraction. Consumes only the
    guest metadata and a compact, already-assembled grounding context - it
    must never perform its own research, browsing, or search."""

    provider_name: str = "unknown"
    model_name: str | None = None

    @abstractmethod
    async def generate(
        self,
        guest: Guest,
        context_items: list[ContentContextItem],
        options: ContentGenerationOptions,
    ) -> ContentGenerationResult:
        raise NotImplementedError
