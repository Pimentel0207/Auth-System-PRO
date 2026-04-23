"""
User service — centralizes user management business logic.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..core.security import hash_password, verify_password
from ..models.models import User


logger = logging.getLogger(__name__)


async def get_user_by_id(session: AsyncSession, user_id: str | UUID) -> User:
    """Fetch a user by ID.

    Raises:
        HTTPException: If user not found.
    """
    # Ensure user_id is a UUID for the database query
    try:
        uid = UUID(user_id) if isinstance(user_id, str) else user_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    statement = select(User).where(User.id == uid)
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def update_user_email(
    session: AsyncSession, user: User, new_email: str
) -> User:
    """Update a user's email.

    Raises:
        HTTPException: If email is already taken.
    """
    # Check if email is already taken
    statement = select(User).where(User.email == new_email)
    result = await session.execute(statement)
    existing = result.scalars().first()

    if existing and str(existing.id) != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already in use",
        )

    user.email = new_email
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def change_password(
    session: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    """Change a user's password.

    Raises:
        HTTPException: If current password is incorrect.
    """
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()
    logger.info("Password changed for user %s", user.id)


async def list_users(
    session: AsyncSession, skip: int = 0, limit: int = 50
) -> list[User]:
    """List all users (admin only)."""
    statement = select(User).offset(skip).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()


async def toggle_user_status(
    session: AsyncSession, user_id: str | UUID, is_active: bool
) -> User:
    """Activate or deactivate a user (admin only).

    Raises:
        HTTPException: If user not found.
    """
    user = await get_user_by_id(session, user_id)
    user.is_active = is_active
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    logger.info("User %s status changed to is_active=%s", user_id, is_active)
    return user
