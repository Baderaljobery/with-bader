from abc import ABC, abstractmethod

from app.design_planning.models import PlanContextItem, SlidePlanGenerationResult, SlidePlanningOptions
from app.models.guest import Guest


class SlidePlanningError(Exception):
    """Base for all slide-planner-layer failures. A provider-specific
    planner (e.g. Groq) raises concrete subclasses; the API layer maps them
    to appropriate HTTP status codes without leaking upstream details."""


class SlidePlannerConfigurationError(SlidePlanningError):
    """Raised when the selected planner is missing required configuration
    (e.g. GROQ_API_KEY). Must never silently fall back."""


class SlidePlannerTimeoutError(SlidePlanningError):
    """Raised when a planner's upstream call exceeds its timeout."""


class SlidePlannerValidationError(SlidePlanningError):
    """Raised when a planner's structured output fails schema validation,
    or does not contain exactly one slide per requested slide_roles entry -
    the caller must never guess/pad a mismatched result."""


class SlidePlanner(ABC):
    """Vendor-agnostic structured slide-copy planning abstraction. Consumes
    only already-selected, already-real context (see context.py) plus the
    user's exact requested slide count/roles - it must never choose the
    slide count, roles, or template itself, and never performs its own
    research/browsing."""

    provider_name: str = "unknown"
    model_name: str | None = None

    @abstractmethod
    async def plan(
        self,
        guest: Guest,
        context_items: list[PlanContextItem],
        options: SlidePlanningOptions,
    ) -> SlidePlanGenerationResult:
        raise NotImplementedError
