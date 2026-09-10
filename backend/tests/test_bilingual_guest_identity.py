import unittest

from app.database.session import SessionLocal
from app.models.guest import Guest
from app.services.guest_service import (
    delete_guest,
    has_complete_bilingual_identity,
    update_guest,
    IncompleteBilingualIdentityError,
)
from app.schemas.guest import GuestUpdate
from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()


def tearDownModule():
    cleanup_client_user(client)


class CreateBilingualGuestApiTests(unittest.TestCase):
    """Phase 2 - the bilingual NAME is required for every NEW guest
    (app/schemas/guest.py GuestCreate). job_title/company/biography stay
    optional, single-value fields, exactly as before this feature existed."""

    def setUp(self):
        self.db = SessionLocal()
        self.created_ids = []

    def tearDown(self):
        for guest_id in self.created_ids:
            try:
                delete_guest(self.db, guest_id)
            except Exception:
                pass
        self.db.close()

    def _payload(self, **overrides):
        payload = {
            "name_ar": "أحمد مثال",
            "name_en": "Ahmed Example",
            "job_title": "رئيس تنفيذي",
            "company": "شركة المثال",
            "biography": "نبذة تعريفية.",
        }
        payload.update(overrides)
        return payload

    def test_create_with_bilingual_name_succeeds(self):
        response = client.post("/api/guests", json=self._payload())
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.created_ids.append(body["id"])
        self.assertEqual(body["name_ar"], "أحمد مثال")
        self.assertEqual(body["name_en"], "Ahmed Example")
        self.assertEqual(body["display_name"], "أحمد مثال")
        # job_title/company/biography stay plain single-value fields.
        self.assertEqual(body["job_title"], "رئيس تنفيذي")
        self.assertEqual(body["company"], "شركة المثال")

    def test_job_title_and_company_and_biography_are_optional(self):
        response = client.post(
            "/api/guests", json={"name_ar": "أحمد", "name_en": "Ahmed"}
        )
        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.created_ids.append(body["id"])
        self.assertIsNone(body["job_title"])
        self.assertIsNone(body["company"])
        self.assertIsNone(body["biography"])

    def _post(self, payload):
        # Tracks any created guest regardless of what the test expected, so
        # a surprise 201 (a validation bug) never leaks a row into the
        # shared dev database instead of failing loudly.
        response = client.post("/api/guests", json=payload)
        if response.status_code == 201:
            self.created_ids.append(response.json()["id"])
        return response

    def test_missing_arabic_name_rejected(self):
        payload = self._payload()
        del payload["name_ar"]
        response = self._post(payload)
        self.assertEqual(response.status_code, 422)

    def test_missing_english_name_rejected(self):
        payload = self._payload()
        del payload["name_en"]
        response = self._post(payload)
        self.assertEqual(response.status_code, 422)

    def test_blank_name_rejected(self):
        payload = self._payload(name_ar="   ")
        response = self._post(payload)
        self.assertEqual(response.status_code, 422)


class LegacyGuestCompatibilityTests(unittest.TestCase):
    """Phase: legacy data / migration safety - a pre-bilingual guest keeps
    working (nullable columns), and display_name falls back to the legacy
    `name` column until the profile is filled in."""

    def setUp(self):
        self.db = SessionLocal()
        # GuestCreate can never produce blank bilingual fields (that's the
        # whole point of the required-field validation), so a legacy row -
        # one that predates the bilingual profile entirely, with NULL
        # bilingual columns - has to be constructed directly against the
        # ORM model, bypassing the schema, the way a real pre-migration row
        # actually looks.
        self.guest = Guest(name="Legacy Name Only", created_by=client.user_id)
        self.db.add(self.guest)
        self.db.commit()
        self.db.refresh(self.guest)

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_display_name_falls_back_to_legacy_name(self):
        self.assertEqual(self.guest.display_name, "Legacy Name Only")

    def test_is_not_complete(self):
        self.assertFalse(has_complete_bilingual_identity(self.guest))

    def test_unrelated_edit_does_not_require_bilingual_profile(self):
        # Editing a field that has nothing to do with the bilingual profile
        # must not suddenly demand it - only touching the profile itself does.
        updated = update_guest(self.db, self.guest.id, GuestUpdate(personal_notes="a note"))
        self.assertEqual(updated.personal_notes, "a note")

    def test_partial_bilingual_edit_is_rejected(self):
        with self.assertRaises(IncompleteBilingualIdentityError):
            update_guest(self.db, self.guest.id, GuestUpdate(name_ar="اسم جديد"))

    def test_full_bilingual_edit_succeeds_and_marks_complete(self):
        updated = update_guest(
            self.db,
            self.guest.id,
            GuestUpdate(name_ar="اسم جديد", name_en="New Name"),
        )
        self.assertTrue(has_complete_bilingual_identity(updated))
        self.assertEqual(updated.display_name, "اسم جديد")


if __name__ == "__main__":
    unittest.main()
