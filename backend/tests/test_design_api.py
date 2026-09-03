import unittest
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.design import _resolve_image_engine, _resolve_planner
from app.design_generation.base import ImageGenerator
from app.design_generation.engine import SlideImageGenerationEngine
from app.design_generation.models import ImageGenerationResult
from app.design_planning.engine import DesignContentPlanner
from app.design_planning.mock import MockSlidePlanner
from app.database.session import SessionLocal
from app.main import app
from app.schemas.content_draft import ContentDraftCreate
from app.schemas.guest import GuestCreate
from app.services import content_service, design_service
from app.services.guest_service import create_guest, delete_guest

client = TestClient(app)


class _FakeImageGenerator(ImageGenerator):
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self):
        self.generate = AsyncMock(
            return_value=ImageGenerationResult(image_bytes=b"fake-png-bytes", mime_type="image/png")
        )

    async def generate(self, prompt, options):  # pragma: no cover - replaced in __init__
        raise NotImplementedError


def _override_dependencies():
    app.dependency_overrides[_resolve_image_engine] = lambda: SlideImageGenerationEngine(
        generator=_FakeImageGenerator()
    )
    app.dependency_overrides[_resolve_planner] = lambda: DesignContentPlanner(planner=MockSlidePlanner())


def _clear_overrides():
    app.dependency_overrides.pop(_resolve_image_engine, None)
    app.dependency_overrides.pop(_resolve_planner, None)


class DesignPlanApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Design Plan API Test Guest"))
        self.content_draft = content_service.create_content_draft(
            self.db,
            self.guest.id,
            ContentDraftCreate(platform="linkedin", length="medium", content="نص محتوى تجريبي للتخطيط."),
        )
        _override_dependencies()

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def _plan_payload(self, **overrides):
        payload = {
            "content_draft_id": str(self.content_draft.id),
            "template_id": "template-01",
            "slide_count": 2,
            "slide_roles": [{"index": 1, "role": "cover"}, {"index": 2, "role": "main_content"}],
            "platform": "linkedin",
        }
        payload.update(overrides)
        return payload

    def test_plan_returns_exactly_requested_slide_count_and_roles(self):
        response = client.post(f"/api/guests/{self.guest.id}/designs/plan", json=self._plan_payload())
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["slides"]), 2)
        self.assertEqual([s["role"] for s in body["slides"]], ["cover", "main_content"])
        self.assertEqual([s["index"] for s in body["slides"]], [1, 2])
        self.assertEqual(body["ai_provider"], "mock")

    def test_plan_does_not_persist_anything(self):
        before = design_service.get_design_drafts(self.db, self.guest.id)
        client.post(f"/api/guests/{self.guest.id}/designs/plan", json=self._plan_payload())
        after = design_service.get_design_drafts(self.db, self.guest.id)
        self.assertEqual(len(before), len(after))

    def test_plan_returns_404_for_unknown_guest(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/api/guests/{fake_id}/designs/plan", json=self._plan_payload())
        self.assertEqual(response.status_code, 404)

    def test_plan_returns_409_for_insufficient_context(self):
        response = client.post(
            f"/api/guests/{self.guest.id}/designs/plan",
            json=self._plan_payload(content_draft_id=None),
        )
        self.assertEqual(response.status_code, 409)

    def test_plan_rejects_unknown_template(self):
        response = client.post(
            f"/api/guests/{self.guest.id}/designs/plan", json=self._plan_payload(template_id="not-real")
        )
        self.assertEqual(response.status_code, 422)

    def test_plan_rejects_role_count_mismatch(self):
        response = client.post(
            f"/api/guests/{self.guest.id}/designs/plan",
            json=self._plan_payload(slide_count=3),  # slide_roles still has 2 entries
        )
        self.assertEqual(response.status_code, 422)

    def test_plan_rejects_more_than_five_slides(self):
        response = client.post(
            f"/api/guests/{self.guest.id}/designs/plan",
            json=self._plan_payload(
                slide_count=6,
                slide_roles=[{"index": i, "role": "main_content"} for i in range(1, 7)],
            ),
        )
        self.assertEqual(response.status_code, 422)

    def test_single_slide_main_content_allowed(self):
        response = client.post(
            f"/api/guests/{self.guest.id}/designs/plan",
            json=self._plan_payload(slide_count=1, slide_roles=[{"index": 1, "role": "main_content"}]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["slides"]), 1)


class DesignCreateAndLifecycleApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Design Lifecycle API Test Guest"))
        self.other_guest = create_guest(self.db, GuestCreate(name="Other Design Guest"))
        self.content_draft = content_service.create_content_draft(
            self.db,
            self.guest.id,
            ContentDraftCreate(platform="linkedin", length="medium", content="نص محتوى تجريبي."),
        )
        _override_dependencies()

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        delete_guest(self.db, self.other_guest.id)
        self.db.close()

    def _create_payload(self, **overrides):
        payload = {
            "content_draft_id": str(self.content_draft.id),
            "template_id": "template-02",
            "slide_count": 3,
            "slides": [
                {"index": 1, "role": "cover", "headline": "عنوان الافتتاحية", "body_text": ""},
                {"index": 2, "role": "main_content", "headline": "عنوان رئيسي", "body_text": "شرح قصير."},
                {"index": 3, "role": "closing", "headline": "خاتمة", "body_text": ""},
            ],
            "platform": "linkedin",
            "aspect_ratio": "1:1",
            "background_color": "#FFFFFF",
            "accent_color": "#1B8FEA",
        }
        payload.update(overrides)
        return payload

    def _create(self, guest_id=None, **overrides):
        target = guest_id or self.guest.id
        return client.post(f"/api/guests/{target}/designs", json=self._create_payload(**overrides))

    def test_create_persists_draft_with_no_images_yet(self):
        response = self._create()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["template_id"], "template-02")
        self.assertEqual(body["slide_count"], 3)
        self.assertEqual(len(body["slides"]), 3)
        self.assertTrue(all(slide["image_path"] is None for slide in body["slides"]))
        self.assertNotIn("prompt", body["slides"][0])
        # Part 24 confirmation: creating a design (the strict template flow)
        # never calls the OpenRouter/Gemini image engine at all - there is
        # simply no provider/model recorded yet.
        self.assertIsNone(body["ai_provider"])
        self.assertIsNone(body["ai_model"])

    def test_create_rejects_unknown_template(self):
        response = self._create(template_id="not-real")
        self.assertEqual(response.status_code, 422)

    def test_create_returns_404_for_unknown_guest(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = self._create(guest_id=fake_id)
        self.assertEqual(response.status_code, 404)

    def test_list_and_get(self):
        created = self._create().json()
        list_response = client.get(f"/api/guests/{self.guest.id}/designs")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        get_response = client.get(f"/api/designs/{created['id']}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["id"], created["id"])

    def test_guest_isolation(self):
        self._create()
        other_response = client.get(f"/api/guests/{self.other_guest.id}/designs")
        self.assertEqual(other_response.json(), [])

    def test_generate_creates_images_for_all_slides(self):
        created = self._create().json()
        response = client.post(f"/api/designs/{created['id']}/generate")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(all(slide["image_path"] for slide in body["slides"]))
        self.assertEqual(body["ai_provider"], "fake")

    def test_generate_only_fills_missing_slides_not_regenerate_existing(self):
        created = self._create().json()
        client.post(f"/api/designs/{created['id']}/generate")
        after_first = client.get(f"/api/designs/{created['id']}").json()
        first_paths = [s["image_path"] for s in after_first["slides"]]

        # Second call to /generate must be a no-op image-wise (all slides
        # already have an image) - cost control (Part 28).
        response = client.post(f"/api/designs/{created['id']}/generate")
        second_paths = [s["image_path"] for s in response.json()["slides"]]
        self.assertEqual(first_paths, second_paths)

    def test_regenerate_all_replaces_every_slide_image(self):
        created = self._create().json()
        client.post(f"/api/designs/{created['id']}/generate")
        before = client.get(f"/api/designs/{created['id']}").json()
        before_paths = [s["image_path"] for s in before["slides"]]

        response = client.post(f"/api/designs/{created['id']}/regenerate-all")
        after_paths = [s["image_path"] for s in response.json()["slides"]]
        self.assertEqual(len(before_paths), len(after_paths))
        for old, new in zip(before_paths, after_paths):
            self.assertNotEqual(old, new)

    def test_regenerate_one_slide_preserves_other_slides(self):
        created = self._create().json()
        client.post(f"/api/designs/{created['id']}/generate")
        before = client.get(f"/api/designs/{created['id']}").json()
        before_by_index = {s["slide_index"]: s for s in before["slides"]}

        response = client.post(f"/api/designs/{created['id']}/slides/2/regenerate", json={})
        self.assertEqual(response.status_code, 200)
        regenerated = response.json()
        self.assertEqual(regenerated["slide_index"], 2)
        self.assertNotEqual(regenerated["image_path"], before_by_index[2]["image_path"])

        after = client.get(f"/api/designs/{created['id']}").json()
        after_by_index = {s["slide_index"]: s for s in after["slides"]}
        self.assertEqual(after_by_index[1]["image_path"], before_by_index[1]["image_path"])
        self.assertEqual(after_by_index[3]["image_path"], before_by_index[3]["image_path"])
        self.assertEqual(after_by_index[2]["image_path"], regenerated["image_path"])

    def test_manual_text_edit_survives_slide_regeneration(self):
        created = self._create().json()
        client.post(f"/api/designs/{created['id']}/generate")

        patch_response = client.patch(
            f"/api/designs/{created['id']}/slides/1",
            json={"headline": "عنوان معدّل يدويًا", "body_text": "نص معدل يدويًا."},
        )
        self.assertEqual(patch_response.status_code, 200)

        regen_response = client.post(f"/api/designs/{created['id']}/slides/1/regenerate", json={})
        self.assertEqual(regen_response.status_code, 200)
        self.assertEqual(regen_response.json()["headline"], "عنوان معدّل يدويًا")
        self.assertEqual(regen_response.json()["body_text"], "نص معدل يدويًا.")

        refetched = client.get(f"/api/designs/{created['id']}").json()
        slide_one = next(s for s in refetched["slides"] if s["slide_index"] == 1)
        self.assertEqual(slide_one["headline"], "عنوان معدّل يدويًا")

    def test_update_shared_draft_fields(self):
        created = self._create().json()
        response = client.patch(
            f"/api/designs/{created['id']}", json={"background_color": "#0B1F3A", "status": "approved"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["background_color"], "#0B1F3A")
        self.assertEqual(response.json()["status"], "approved")

    def test_delete_design_removes_it(self):
        created = self._create().json()
        response = client.delete(f"/api/designs/{created['id']}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(client.get(f"/api/designs/{created['id']}").status_code, 404)

    def test_regenerate_slide_returns_404_for_unknown_slide_index(self):
        created = self._create().json()
        response = client.post(f"/api/designs/{created['id']}/slides/99/regenerate", json={})
        self.assertEqual(response.status_code, 404)

    def test_slide_count_one_to_five_all_creatable(self):
        for count in range(1, 6):
            slides = [
                {"index": i, "role": "main_content", "headline": f"عنوان {i}", "body_text": ""}
                for i in range(1, count + 1)
            ]
            response = self._create(slide_count=count, slides=slides)
            self.assertEqual(response.status_code, 201, msg=f"slide_count={count} failed: {response.text}")
            self.assertEqual(len(response.json()["slides"]), count)

    def test_slide_ordering_is_preserved_regardless_of_input_order(self):
        slides = [
            {"index": 3, "role": "closing", "headline": "ثالث", "body_text": ""},
            {"index": 1, "role": "cover", "headline": "أول", "body_text": ""},
            {"index": 2, "role": "main_content", "headline": "ثاني", "body_text": ""},
        ]
        response = self._create(slide_count=3, slides=slides)
        indices = [s["slide_index"] for s in response.json()["slides"]]
        self.assertEqual(indices, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
