"""Password hashing (Argon2id) and session-token (JWT) primitives. No
session table - a signed, expiring token carries the user id, verified
statelessly on every request (see app/core/auth.py for how it's read from
an HttpOnly cookie)."""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_JWT_ALGORITHM = "HS256"

_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        # Any malformed/legacy hash is treated as "does not match" rather
        # than propagating a 500 - never leak hashing internals to a client.
        return False


def create_session_token(user_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.auth_token_expire_minutes),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=_JWT_ALGORITHM)


def decode_session_token(token: str) -> uuid.UUID | None:
    """Returns the user id encoded in a valid, unexpired token, or `None`
    for anything invalid/expired/tampered - callers treat that uniformly
    as "not authenticated"."""
    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=[_JWT_ALGORITHM])
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
