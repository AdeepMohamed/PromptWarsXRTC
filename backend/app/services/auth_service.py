from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.learner import LearnerProfile
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister, UserLogin, AuthResponse, UserResponse
from fastapi import HTTPException, status
import uuid


async def register_user(db: AsyncSession, data: UserRegister) -> AuthResponse:
    # Check if email exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username exists
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()

    # Create learner profile
    profile = LearnerProfile(user_id=user.id)
    db.add(profile)
    await db.flush()

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})

    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, username=user.username, full_name=user.full_name),
        access_token=token,
    )


async def login_user(db: AsyncSession, data: UserLogin) -> AuthResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})

    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, username=user.username, full_name=user.full_name),
        access_token=token,
    )
