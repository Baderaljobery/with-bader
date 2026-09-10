import unittest

from app.api.design import _resolve_planner
from app.design_planning.engine import DesignContentPlanner
from app.design_planning.mock import MockSlidePlanner
from app.database.session import SessionLocal
from app.main import app
from app.schemas.content_draft import ContentDraftCreate

from app.services import content_service, design_service
from app.services.guest_service import create_guest, delete_guest
from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client
from tests.db_test_helpers import make_guest_create

client = make_authenticated_client()

def _override_dependencies():
    app.dependency_overrides[_resolve_planner] = lambda: DesignContentPlanner(planner=MockSlidePlanner())

def _clear_overrides():
    app.dependency_overrides.pop(_resolve_planner, None)

class DesignPlanApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, make_guest_create(name="Design Plan API Test Guest"), created_by=client.user_id)
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
        self.guest = create_guest(self.db, make_guest_create(name="Design Lifecycle API Test Guest"), created_by=client.user_id)
        self.other_guest = create_guest(self.db, make_guest_create(name="Other Design Guest"), created_by=client.user_id)
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
        # Creating a design (the strict template flow) never calls an AI
        # image engine at all - there is simply no provider/model recorded.
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

    def test_update_shared_draft_fields(self):
        created = self._create().json()
        response = client.patch(
            f"/api/designs/{created['id']}", json={"background_color": "#0B1F3A", "status": "approved"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["background_color"], "#0B1F3A")
        self.assertEqual(response.json()["status"], "approved")

    def test_create_without_cta_text_persists_as_null(self):
        """cta_text is genuinely optional end-to-end - omitting it entirely
        from a slide must not be rejected or coerced into an empty string."""
        created = self._create().json()
        self.assertTrue(all(slide["cta_text"] is None for slide in created["slides"]))

    def test_create_with_cta_text_persists_it(self):
        payload = self._create_payload(
            slides=[{"index": 1, "role": "cover", "headline": "عنوان", "body_text": "", "cta_text": "تابعنا"}],
            slide_count=1,
        )
        response = client.post(f"/api/guests/{self.guest.id}/designs", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["slides"][0]["cta_text"], "تابعنا")

    def test_update_slide_with_explicit_null_cta_clears_it(self):
        created = self._create(
            slides=[{"index": 1, "role": "cover", "headline": "عنوان", "body_text": "", "cta_text": "تابعنا"}],
            slide_count=1,
        ).json()

        response = client.patch(
            f"/api/designs/{created['id']}/slides/1",
            json={"headline": "رؤيتي في إدارة الموظفين", "body_text": "نص الجسم.", "cta_text": None},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsNone(body["cta_text"])
        self.assertEqual(body["headline"], "رؤيتي في إدارة الموظفين")
        self.assertEqual(body["body_text"], "نص الجسم.")

    def test_saved_null_cta_survives_a_refetch(self):
        created = self._create(
            slides=[{"index": 1, "role": "cover", "headline": "عنوان", "body_text": "", "cta_text": "تابعنا"}],
            slide_count=1,
        ).json()
        client.patch(f"/api/designs/{created['id']}/slides/1", json={"cta_text": None})

        refetched = client.get(f"/api/designs/{created['id']}").json()
        self.assertIsNone(refetched["slides"][0]["cta_text"])

    def test_update_slide_without_cta_field_leaves_existing_cta_untouched(self):
        """exclude_unset semantics: omitting cta_text from the PATCH body
        entirely must not be confused with explicitly clearing it."""
        created = self._create(
            slides=[{"index": 1, "role": "cover", "headline": "عنوان", "body_text": "", "cta_text": "تابعنا"}],
            slide_count=1,
        ).json()

        response = client.patch(f"/api/designs/{created['id']}/slides/1", json={"headline": "عنوان جديد"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["cta_text"], "تابعنا")

    def test_delete_design_removes_it(self):
        created = self._create().json()
        response = client.delete(f"/api/designs/{created['id']}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(client.get(f"/api/designs/{created['id']}").status_code, 404)

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

def tearDownModule():
    cleanup_client_user(client)
