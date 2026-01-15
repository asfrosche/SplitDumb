"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.schemas import UserRegister, UserLogin, AuthResponse, UserResponse
from app.application.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)
    try:
        user, token = auth_service.register(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            default_currency=user_data.default_currency,
        )
        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=token,
            token_type="bearer",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get JWT token."""
    auth_service = AuthService(db)
    result = auth_service.login(email=credentials.email, password=credentials.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    user, token = result
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=token,
        token_type="bearer",
    )
