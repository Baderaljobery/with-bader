from abc import ABC, abstractmethod

from app.models.guest import Guest
from app.research.models import NormalizedResearchSource, ResearchExtractionResult


class ResearchExtractionError(Exception):
    """Base for all extractor-layer failures. A provider-specific extractor
    (e.g. Groq) raises concrete subclasses; the API layer maps them to
    appropriate HTTP status codes without leaking upstream details."""


class ResearchExtractorConfigurationError(ResearchExtractionError):
    """Raised when RESEARCH_EXTRACTOR_PROVIDER is unset/unsupported, or the
    selected extractor is missing required configuration (e.g. an API key).
    Must never silently fall back - the caller needs to know real
    extraction did not run."""


class ResearchExtractorTimeoutError(ResearchExtractionError):
    """Raised when an extractor's upstream call exceeds its timeout."""


class ResearchExtractorValidationError(ResearchExtractionError):
    """Raised when an extractor's structured output fails schema/Pydantic
    validation and cannot be trusted enough to persist."""


class ResearchExtractor(ABC):
    """AI-provider-agnostic extraction abstraction. The engine depends only on this."""

    provider_name: str = "unknown"
    model_name: str | None = None

    @abstractmethod
    async def extract(
        self, guest: Guest, sources: list[NormalizedResearchSource]
    ) -> ResearchExtractionResult:
        raise NotImplementedError
