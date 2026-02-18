"""
Authentication endpoints for AI Podcast Platform
"""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field, EmailStr

from app.database import get_session
from app.models import User
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user_required,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    name: str = Field(..., min_length=1, max_length=100, description="Display name")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class UserProfileResponse(BaseModel):
    id: str
    email: str
    is_active: bool


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new user account.

    - **email**: Valid email address
    - **password**: Password (minimum 8 characters)
    - **name**: Display name
    """
    # Check if email already exists
    result = await session.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(data.password)
    user = User(
        email=data.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"New user registered: {user.email}")

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id),
        email=str(user.email),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """
    Login with email and password.

    Returns a JWT access token.
    """
    user = await authenticate_user(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id),
        email=str(user.email),
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user_required)):
    """Get current user profile"""
    return UserProfileResponse(
        id=str(current_user.id),
        email=str(current_user.email),
        is_active=bool(current_user.is_active),
    )


@router.post("/logout")
async def logout():
    """
    Logout (client should discard the token).
    JWT tokens are stateless, so server-side logout just returns success.
    """
    return {"message": "Successfully logged out"}
