import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.design_planning.base import SlidePlanner
from app.design_planning.context import gather_slide_planning_context, has_sufficient_context
from app.design_planning.models import PlanContextItem, PlannedSlideResult, SlidePlanningOptions
from app.models.guest import Guest
from app.services import guest_service


class PlanContextInsufficientError(Exception):
    """Raised when none of content_draft_id/question_ids/notebook_block_ids
    resolved to any real, usable source material - there is nothing
    grounded to plan slides from, so no Groq call is made."""


@dataclass
class DesignPlanRunResult:
    guest: Guest
    planner_provider: str
    planner_model: str | None
    context_items: list[PlanContextItem]
    slides: list[PlannedSlideResult]


class DesignContentPlanner:
    """Turns user-selected real source material into structured slide copy
    for the EXACT slide count/roles the user chose. Never decides slide
    count, roles, or template itself - those are always inputs, not
    outputs (see Part 8 of the Design Engine rework spec)."""

    def __init__(self, planner: SlidePlanner) -> None:
        self._planner = planner

    async def plan_slides(
        self,
        guest_id: uuid.UUID,
        db: Session,
        content_draft_id: uuid.UUID | None,
        question_ids: list[uuid.UUID],
        notebook_block_ids: list[uuid.UUID],
        options: SlidePlanningOptions,
    ) -> DesignPlanRunResult:
        guest = guest_service.get_guest_by_id(db, guest_id)

        context_items = gather_slide_planning_context(
            db, guest_id, content_draft_id, question_ids, notebook_block_ids
        )
        if not has_sufficient_context(context_items):
            raise PlanContextInsufficientError(
                f"No selected content draft, answered questions, or notebook blocks available to "
                f"plan slides from for guest '{guest_id}'"
            )

        result = await self._planner.plan(guest, context_items, options)

        return DesignPlanRunResult(
            guest=guest,
            planner_provider=self._planner.provider_name,
            planner_model=self._planner.model_name,
            context_items=context_items,
            slides=result.slides,
        )


def get_design_content_planner() -> DesignContentPlanner:
    from app.design_planning.factory import build_slide_planner

    return DesignContentPlanner(planner=build_slide_planner())
