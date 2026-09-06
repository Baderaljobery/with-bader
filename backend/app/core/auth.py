"""The one reusable authentication dependency (`get_current_user`) plus the
cookie helpers used by the auth endpoints. Every private route depends on
`get_current_user` - no endpoint parses the session token itself."""

from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_session_token
from app.database.session import get_db
from app.models.user import User
from app.services import user_service


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Reads the session cookie, validates it, and loads the user - raises
    401 for anything short of a fully valid session (missing cookie,
    expired/tampered token, or a user id that no longer exists). Never
    distinguishes these cases in the response, so nothing about *why* auth
    failed is leaked."""
    token = request.cookies.get(settings.auth_cookie_name)
    user_id = decode_session_token(token) if token else None
    user = user_service.get_user_by_id(db, user_id) if user_id else None

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.auth_token_expire_minutes * 60,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )
