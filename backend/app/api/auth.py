from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import clear_session_cookie, get_current_user, set_session_cookie
from app.core.rate_limit import enforce_login_rate_limit, enforce_registration_request
from app.core.security import create_session_token
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services import user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(enforce_registration_request),
) -> UserResponse:
    """Auto-authenticates on success (Part 4) - registering and logging in
    are the same request, no separate login step required."""
    try:
        user = user_service.create_user(db, name=payload.name, email=payload.email, password=payload.password)
    except user_service.EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc

    set_session_cookie(response, create_session_token(user.id))
    return user


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(enforce_login_rate_limit),
) -> UserResponse:
    user = user_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        # Same message whether the email doesn't exist or the password is
        # wrong - never lets a caller distinguish the two (Part 5).
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    set_session_cookie(response, create_session_token(user.id))
    return user


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    clear_session_cookie(response)


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    response: Response, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    """Deletes the authenticated user and every Guest (and everything
    beneath it) that they own - see user_service.delete_user_account for
    exactly how that cascade is guaranteed. Never affects any other
    user's data."""
    user_service.delete_user_account(db, current_user.id)
    clear_session_cookie(response)
