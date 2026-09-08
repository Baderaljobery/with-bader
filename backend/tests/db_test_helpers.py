import uuid

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


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
