"""
User repository for database operations.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.models import User


class UserRepository:
    """Repository for user operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, password_hash: str, name: str, default_currency: str = "USD") -> User:
        """Create a new user."""
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            default_currency=default_currency,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
