import unittest

from app.design_planning.base import SlidePlanner
from app.design_planning.engine import DesignContentPlanner, PlanContextInsufficientError
from app.design_planning.models import SlidePlanningOptions, SlideRoleSpec
from app.design_planning.mock import MockSlidePlanner
from app.database.session import SessionLocal
from app.schemas.content_draft import ContentDraftCreate
from app.schemas.guest import GuestCreate
from app.services import content_service
from app.services.guest_service import create_guest, delete_guest
from tests.db_test_helpers import create_test_owner, delete_test_owner


def _options(**overrides):
    defaults = dict(
        platform="linkedin",
        slide_roles=[SlideRoleSpec(index=1, role="main_content")],
        template_id="template-01",
    )
    defaults.update(overrides)
    return SlidePlanningOptions(**defaults)


class DesignContentPlannerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.owner = create_test_owner(self.db)
        self.guest = create_guest(
            self.db, GuestCreate(name="Design Content Planner Test Guest"), self.owner.id
        )
        self.planner = DesignContentPlanner(planner=MockSlidePlanner())

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        delete_test_owner(self.db, self.owner)
        self.db.close()

    async def test_no_selection_raises_insufficient_context(self):
        with self.assertRaises(PlanContextInsufficientError):
            await self.planner.plan_slides(self.guest.id, self.db, None, [], [], _options())

    async def test_content_draft_selection_produces_exactly_requested_slides(self):
        draft = content_service.create_content_draft(
            self.db, self.guest.id, ContentDraftCreate(platform="linkedin", length="medium", content="نص")
        )
        options = _options(
            slide_roles=[
                SlideRoleSpec(index=1, role="cover"),
                SlideRoleSpec(index=2, role="main_content"),
                SlideRoleSpec(index=3, role="closing"),
            ]
        )
        result = await self.planner.plan_slides(self.guest.id, self.db, draft.id, [], [], options)

        self.assertEqual(len(result.slides), 3)
        self.assertEqual([s.role for s in result.slides], ["cover", "main_content", "closing"])
        self.assertEqual([s.index for s in result.slides], [1, 2, 3])
        self.assertEqual(result.planner_provider, "mock")

    async def test_single_slide_main_content_is_allowed_without_cover(self):
        draft = content_service.create_content_draft(
            self.db, self.guest.id, ContentDraftCreate(platform="x", length="short", content="نص قصير")
        )
        result = await self.planner.plan_slides(
            self.guest.id, self.db, draft.id, [], [], _options(slide_roles=[SlideRoleSpec(index=1, role="main_content")])
        )
        self.assertEqual(len(result.slides), 1)
        self.assertEqual(result.slides[0].role, "main_content")


class RaisingPlanner(SlidePlanner):
    provider_name = "raising"

    async def plan(self, guest, context_items, options):
        raise AssertionError("plan() must never be called when context is insufficient")


class DesignContentPlannerNeverCallsProviderWhenInsufficientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.owner = create_test_owner(self.db)
        self.guest = create_guest(
            self.db, GuestCreate(name="Design Content Planner Guard Test Guest"), self.owner.id
        )

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        delete_test_owner(self.db, self.owner)
        self.db.close()

    async def test_provider_is_never_called_without_selected_context(self):
        planner = DesignContentPlanner(planner=RaisingPlanner())
        with self.assertRaises(PlanContextInsufficientError):
            await planner.plan_slides(self.guest.id, self.db, None, [], [], _options())


if __name__ == "__main__":
    unittest.main()
