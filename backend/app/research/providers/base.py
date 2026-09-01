from abc import ABC, abstractmethod

from app.research.models import RawResearchSource


class ResearchProviderError(Exception):
    """Raised when a search provider fails to return results."""


class ResearchProviderConfigurationError(ResearchProviderError):
    """Raised when a search provider is selected but not configured correctly
    (e.g. a required API key is missing). Must never fall back to a mock
    silently - the caller needs to know real research did not run."""


class ResearchProviderTimeoutError(ResearchProviderError):
    """Raised when a search provider call exceeds its timeout."""


class ResearchSearchProvider(ABC):
    """Vendor-agnostic search abstraction. The engine depends only on this.

    fallback_provider_name / fallback_queries_used are optional metadata a
    provider may expose about itself (a plain provider leaves them at their
    defaults; a fallback-wrapping provider populates them). The engine reads
    these generically - it never needs to know a specific wrapper exists.
    """

    provider_name: str = "unknown"
    fallback_provider_name: str | None = None
    fallback_queries_used: int = 0

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[RawResearchSource]:
        raise NotImplementedError
