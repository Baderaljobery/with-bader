"""Shared helper for tests that hit the HTTP API through TestClient. Every
application-data endpoint now requires a real authenticated session (see
app/core/auth.py), so any test using TestClient needs a logged-in user
before it can exercise them."""

import uuid

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
from app.models.user import User


def make_authenticated_client(name: str = "Test Fixture User") -> TestClient:
    """A fresh TestClient with its own fresh test user already registered
    (which auto-authenticates and sets the session cookie - see
    POST /api/auth/register). TestClient persists cookies across requests
    made on the same instance, so every subsequent call on the returned
    client is already authenticated as this user.

    Each call creates a brand-new, isolated user with a unique email, so
    tests never accidentally share ownership of the same guests. The new
    user's id and email are attached as `client.user_id`/`client.email` -
    tests that create fixture guests directly via guest_service (bypassing
    the HTTP API) need `client.user_id` as `created_by`, or every scoped
    list/detail call would 404/exclude them; `client.email` lets a test
    log the same user back in directly."""
    client = TestClient(app)
    email = f"test-{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": "testpassword123"},
    )
    assert response.status_code == 201, response.text
    client.user_id = uuid.UUID(response.json()["id"])
    client.email = email
    client.password = "testpassword123"
    return client


def cleanup_client_user(client: TestClient) -> None:
    """Deletes a make_authenticated_client() user directly at the DB level
    (bypassing the delete-account endpoint, which also cascades any guests
    a test created for that user) - call this from a module-level
    `tearDownModule()` wherever `client = make_authenticated_client()` is
    a module-level fixture, so the real dev database never accumulates
    leftover test-*@example.com accounts across test runs (Part 38)."""
    db = SessionLocal()
    try:
        user = db.get(User, client.user_id)
        if user is not None:
            db.delete(user)
            db.commit()
    finally:
        db.close()
