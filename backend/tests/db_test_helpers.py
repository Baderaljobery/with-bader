import uuid

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.guest import GuestCreate

# Placeholder bilingual name for tests that only care about some OTHER
# feature (interview, notebook, statistics, questions, ...) and just need
# *a* valid guest to hang their fixtures on - GuestCreate requires name_ar/
# name_en (the only bilingual identity field). This is obviously-synthetic
# test data, never real guest information, and every field can still be
# overridden per-test via **overrides.
_DEFAULT_BILINGUAL_IDENTITY = {
    "name_ar": "ضيف اختبار",
    "name_en": "Test Guest",
}


def make_guest_create(name: str | None = None, **overrides) -> GuestCreate:
    """A fully-valid GuestCreate for tests that don't care about the
    bilingual name itself - fills the required name_ar/name_en with
    placeholder test data, then applies **overrides (including job_title/
    company/biography/name_ar/name_en directly, for tests that DO care)."""
    fields = dict(_DEFAULT_BILINGUAL_IDENTITY)
    if name is not None:
        fields["name_ar"] = name
        fields["name_en"] = name
    fields.update(overrides)
    return GuestCreate(**fields)


class FakeGuestIdentity:
    """A minimal, DB-free stand-in for a Guest ORM instance for unit tests
    that need SOME identity attributes to exist (even if blank) -
    app/research/identity_resolution.py and
    app/research/extraction/source_selector.py read these directly (not via
    getattr), since a real Guest row always has them, just possibly None."""

    def __init__(self, **overrides) -> None:
        defaults = {
            "name_ar": "",
            "name_en": "",
            "name": "",
            "job_title": "",
            "company": "",
        }
        defaults.update(overrides)
        for key, value in defaults.items():
            setattr(self, key, value)


def create_test_owner(db: Session) -> User:
    user = User(
        name="Test Owner",
        email=f"db-test-{uuid.uuid4()}@example.com",
        password_hash=hash_password("testpassword123"),
        role="owner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_test_owner(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
