"""
Application service for authentication operations.
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.db.models import User


class AuthService:
    """Application service for authentication."""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db

    def register(self, email: str, password: str, name: str, default_currency: str = "USD") -> tuple[User, str]:
        """Register a new user and return user with JWT token."""
        # Check if user exists
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        # Create user
        password_hash = get_password_hash(password)
        user = self.user_repo.create(email, password_hash, name, default_currency)

        # Generate token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        return user, token

    def login(self, email: str, password: str) -> Optional[tuple[User, str]]:
        """Authenticate user and return user with JWT token."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        return user, token

    def get_current_user(self, user_id: int) -> Optional[User]:
        """Get current user by ID."""
        return self.user_repo.get_by_id(user_id)
