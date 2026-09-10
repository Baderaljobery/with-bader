import unittest
import uuid
from types import SimpleNamespace

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.pagination import PaginationParams
from app.core.rate_limit import (
    enforce_ai_rate_limit,
    enforce_login_rate_limit,
    enforce_registration_request,
    rate_limiter,
)
from app.main import app as production_app
from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        rate_limiter.reset()
        self.originals = {
            "login_rate_limit": settings.login_rate_limit,
            "login_rate_window_seconds": settings.login_rate_window_seconds,
            "register_rate_limit": settings.register_rate_limit,
            "register_rate_window_seconds": settings.register_rate_window_seconds,
            "ai_rate_limit": settings.ai_rate_limit,
            "ai_rate_window_seconds": settings.ai_rate_window_seconds,
            "registration_mode": settings.registration_mode,
        }

    def tearDown(self):
        for name, value in self.originals.items():
            setattr(settings, name, value)
        rate_limiter.reset()

    def test_login_is_limited_per_ip_and_returns_retry_after(self):
        settings.login_rate_limit = 1
        test_app = FastAPI()

        @test_app.post("/login")
        def login(_: None = Depends(enforce_login_rate_limit)):
            return {"ok": True}

        client = TestClient(test_app)
        self.assertEqual(client.post("/login").status_code, 200)
        blocked = client.post("/login")
        self.assertEqual(blocked.status_code, 429)
        self.assertIn("retry-after", blocked.headers)

    def test_registration_can_be_closed_without_code_changes(self):
        settings.registration_mode = "closed"
        test_app = FastAPI()

        @test_app.post("/register")
        def register(_: None = Depends(enforce_registration_request)):
            return {"ok": True}

        response = TestClient(test_app).post("/register")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Registration is disabled")

    def test_registration_is_limited_per_ip(self):
        settings.registration_mode = "open"
        settings.register_rate_limit = 1
        test_app = FastAPI()

        @test_app.post("/register")
        def register(_: None = Depends(enforce_registration_request)):
            return {"ok": True}

        client = TestClient(test_app)
        self.assertEqual(client.post("/register").status_code, 200)
        self.assertEqual(client.post("/register").status_code, 429)

    def test_ai_limit_is_scoped_per_user(self):
        settings.ai_rate_limit = 1
        first_user = SimpleNamespace(id=uuid.uuid4())
        second_user = SimpleNamespace(id=uuid.uuid4())
        active_user = {"value": first_user}
        test_app = FastAPI()
        test_app.dependency_overrides[get_current_user] = lambda: active_user["value"]

        @test_app.post("/ai")
        def ai(user=Depends(enforce_ai_rate_limit)):
            return {"id": str(user.id)}

        client = TestClient(test_app)
        self.assertEqual(client.post("/ai").status_code, 200)
        self.assertEqual(client.post("/ai").status_code, 429)
        active_user["value"] = second_user
        self.assertEqual(client.post("/ai").status_code, 200)


class RequestConfigurationTests(unittest.TestCase):
    def test_pagination_bounds_and_parameter_names_are_api_compatible(self):
        test_app = FastAPI()

        @test_app.get("/items")
        def items(pagination: PaginationParams = Depends()):
            return {"skip": pagination.skip, "limit": pagination.limit}

        client = TestClient(test_app)
        self.assertEqual(client.get("/items?skip=2&limit=3").json(), {"skip": 2, "limit": 3})
        self.assertEqual(client.get("/items?skip=-1").status_code, 422)
        self.assertEqual(client.get("/items?limit=101").status_code, 422)

    def test_cors_uses_configured_local_defaults(self):
        client = TestClient(production_app)
        allowed = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        denied = client.options(
            "/health",
            headers={
                "Origin": "https://unconfigured.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.headers["access-control-allow-origin"], "http://localhost:3000")
        self.assertEqual(denied.status_code, 400)


class PaginationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = make_authenticated_client()

    def tearDown(self):
        cleanup_client_user(self.client)

    def test_guest_collection_applies_skip_and_limit(self):
        for index in range(3):
            response = self.client.post(
                "/api/guests",
                json={
                    "name_ar": f"ضيف صفحات {index}",
                    "name_en": f"Paged Guest {index}",
                },
            )
            self.assertEqual(response.status_code, 201, response.text)

        response = self.client.get("/api/guests?skip=1&limit=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(self.client.get("/api/guests?limit=101").status_code, 422)


if __name__ == "__main__":
    unittest.main()
