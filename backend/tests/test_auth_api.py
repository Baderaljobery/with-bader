import unittest
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.database.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def _unique_email() -> str:
    return f"auth-test-{uuid.uuid4()}@example.com"


class RegisterTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.created_user_ids: list[uuid.UUID] = []

    def tearDown(self):
        for user_id in self.created_user_ids:
            user = self.db.get(User, user_id)
            if user is not None:
                self.db.delete(user)
                self.db.commit()
        self.db.close()

    def _register(self, **overrides):
        payload = {"name": "مستخدم اختبار", "email": _unique_email(), "password": "testpassword123"}
        payload.update(overrides)
        return TestClient(app).post("/api/auth/register", json=payload)

    def test_new_email_succeeds_and_password_is_never_returned(self):
        response = self._register()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.created_user_ids.append(uuid.UUID(body["id"]))
        self.assertEqual(body["name"], "مستخدم اختبار")
        self.assertNotIn("password", body)
        self.assertNotIn("password_hash", body)

    def test_password_is_stored_hashed_not_plaintext(self):
        email = _unique_email()
        response = self._register(email=email, password="a-real-password-123")
        self.created_user_ids.append(uuid.UUID(response.json()["id"]))

        user = self.db.scalars(select(User).where(User.email == email)).first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, "a-real-password-123")
        self.assertTrue(user.password_hash.startswith("$argon2"))

    def test_duplicate_email_is_rejected_with_409(self):
        email = _unique_email()
        first = self._register(email=email)
        self.created_user_ids.append(uuid.UUID(first.json()["id"]))

        second = self._register(email=email)
        self.assertEqual(second.status_code, 409)

    def test_email_is_case_and_whitespace_normalized_for_uniqueness(self):
        email = _unique_email()
        first = self._register(email=email)
        self.created_user_ids.append(uuid.UUID(first.json()["id"]))

        second = self._register(email=f"  {email.upper()}  ")
        self.assertEqual(second.status_code, 409)

    def test_password_too_short_is_rejected(self):
        response = self._register(password="short")
        self.assertEqual(response.status_code, 422)

    def test_auto_login_sets_session_cookie_and_me_works(self):
        fresh_client = TestClient(app)
        email = _unique_email()
        response = fresh_client.post(
            "/api/auth/register",
            json={"name": "مستخدم اختبار", "email": email, "password": "testpassword123"},
        )
        self.created_user_ids.append(uuid.UUID(response.json()["id"]))
        self.assertIn(settings.auth_cookie_name, response.cookies)

        me = fresh_client.get("/api/auth/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], email)


class LoginTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.email = _unique_email()
        self.password = "testpassword123"
        response = TestClient(app).post(
            "/api/auth/register",
            json={"name": "ضيف تسجيل الدخول", "email": self.email, "password": self.password},
        )
        self.user_id = uuid.UUID(response.json()["id"])

    def tearDown(self):
        user = self.db.get(User, self.user_id)
        if user is not None:
            self.db.delete(user)
            self.db.commit()
        self.db.close()

    def test_correct_credentials_succeed(self):
        response = TestClient(app).post(
            "/api/auth/login", json={"email": self.email, "password": self.password}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], self.email)

    def _login(self, **overrides):
        payload = {"email": self.email, "password": self.password}
        payload.update(overrides)
        return TestClient(app).post("/api/auth/login", json=payload)

    def test_wrong_password_fails_with_generic_message(self):
        response = self._login(password="wrong-password")
        self.assertEqual(response.status_code, 401)

    def test_unknown_email_fails_with_the_same_generic_message(self):
        wrong_password_response = self._login(password="wrong-password")
        unknown_email_response = self._login(email=_unique_email(), password="whatever123")

        self.assertEqual(unknown_email_response.status_code, 401)
        # Identical message for "wrong password" and "no such account" - never
        # lets a caller distinguish the two (Part 5).
        self.assertEqual(unknown_email_response.json()["detail"], wrong_password_response.json()["detail"])

    def test_login_sets_a_working_session_cookie(self):
        fresh_client = TestClient(app)
        fresh_client.post("/api/auth/login", json={"email": self.email, "password": self.password})
        me = fresh_client.get("/api/auth/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["id"], str(self.user_id))


class ProtectedEndpointTests(unittest.TestCase):
    def test_me_requires_authentication(self):
        response = TestClient(app).get("/api/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_guests_list_requires_authentication(self):
        response = TestClient(app).get("/api/guests")
        self.assertEqual(response.status_code, 401)

    def test_statistics_requires_authentication(self):
        response = TestClient(app).get("/api/statistics/overview")
        self.assertEqual(response.status_code, 401)

    def test_calendar_requires_authentication(self):
        response = TestClient(app).get(
            "/api/calendar/events", params={"start": "2026-01-01", "end": "2026-01-31"}
        )
        self.assertEqual(response.status_code, 401)

    def test_garbage_cookie_value_is_rejected(self):
        forged_client = TestClient(app)
        forged_client.cookies.set(settings.auth_cookie_name, "not-a-real-token")
        response = forged_client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_health_and_docs_stay_public(self):
        self.assertEqual(TestClient(app).get("/health").status_code, 200)
        self.assertEqual(TestClient(app).get("/docs").status_code, 200)


class LogoutTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.email = _unique_email()
        self.client = TestClient(app)
        response = self.client.post(
            "/api/auth/register",
            json={"name": "ضيف تسجيل الخروج", "email": self.email, "password": "testpassword123"},
        )
        self.user_id = uuid.UUID(response.json()["id"])

    def tearDown(self):
        user = self.db.get(User, self.user_id)
        if user is not None:
            self.db.delete(user)
            self.db.commit()
        self.db.close()

    def test_logout_then_me_and_protected_endpoints_become_401(self):
        self.assertEqual(self.client.get("/api/auth/me").status_code, 200)

        logout_response = self.client.post("/api/auth/logout")
        self.assertEqual(logout_response.status_code, 204)

        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)
        self.assertEqual(self.client.get("/api/guests").status_code, 401)


if __name__ == "__main__":
    unittest.main()
