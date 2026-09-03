from app.design_planning.base import SlidePlanner
from app.design_planning.models import (
    PlanContextItem,
    PlannedSlideResult,
    SlidePlanGenerationResult,
    SlidePlanningOptions,
)
from app.models.guest import Guest


class MockSlidePlanner(SlidePlanner):
    """Deterministic, no-network planner for tests and local dev. Derives
    slide text only from guest.name and the first context item's text, so
    output is stable and inspectable - not meant to be good copy."""

    provider_name = "mock"
    model_name = "mock-planner-v1"

    async def plan(
        self,
        guest: Guest,
        context_items: list[PlanContextItem],
        options: SlidePlanningOptions,
    ) -> SlidePlanGenerationResult:
        seed = context_items[0].text[:80] if context_items else guest.name

        slides = [
            PlannedSlideResult(
                index=spec.index,
                role=spec.role,
                headline=f"{guest.name} - {spec.role} {spec.index}",
                body_text=seed,
                cta_text=None,
            )
            for spec in options.slide_roles
        ]
        return SlidePlanGenerationResult(slides=slides)
