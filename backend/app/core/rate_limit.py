"""Small, thread-safe sliding-window limits for the single-process API.

The deployment configuration deliberately runs one Uvicorn process. If the
application later scales to multiple API processes or hosts, replace this
store with a shared backend (for example Redis) without changing endpoints.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Depends, HTTPException, Request, status

from app.core.auth import get_current_user
from app.core.config import settings
from app.models.user import User


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def retry_after(self, key: str, limit: int, window_seconds: int) -> int | None:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                return max(1, math.ceil(events[0] + window_seconds - now))
            events.append(now)
            return None

    def reset(self) -> None:
        """Clear state; used by tests and safe operational reloads."""
        with self._lock:
            self._events.clear()


rate_limiter = SlidingWindowRateLimiter()


def _client_ip(request: Request) -> str:
    # Do not trust X-Forwarded-For by default: clients can spoof it unless a
    # trusted proxy is configured to sanitize that header.
    return request.client.host if request.client else "unknown"


def _enforce(key: str, limit: int, window_seconds: int) -> None:
    retry_after = rate_limiter.retry_after(key, limit, window_seconds)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers={"Retry-After": str(retry_after)},
        )


def enforce_login_rate_limit(request: Request) -> None:
    _enforce(
        f"login:{_client_ip(request)}",
        settings.login_rate_limit,
        settings.login_rate_window_seconds,
    )


def enforce_registration_request(request: Request) -> None:
    if settings.registration_mode == "closed":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled",
        )
    _enforce(
        f"register:{_client_ip(request)}",
        settings.register_rate_limit,
        settings.register_rate_window_seconds,
    )


def enforce_ai_rate_limit(current_user: User = Depends(get_current_user)) -> User:
    _enforce(
        f"ai:{current_user.id}",
        settings.ai_rate_limit,
        settings.ai_rate_window_seconds,
    )
    return current_user
