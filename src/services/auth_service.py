"""
Authentication service — centralizes all auth business logic.

This module extracts the auth logic from the routes, eliminating
code duplication and making the codebase testable and maintainable.
"""
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..core.config import settings
from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    needs_rehash,
    verify_password,
)
from ..models.models import ActivityLog, RefreshToken, User


logger = logging.getLogger(__name__)


def _hash_token(token: str) -> str:
    """Hash a token using SHA-256 for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


async def _log_activity(
    session: AsyncSession,
    user_id: UUID | None,
    action: str,
    ip_address: str | None,
    user_agent: str | None,
    activity_status: str,
) -> None:
    """Log user activity to the database."""
    log = ActivityLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        status=activity_status,
    )
    session.add(log)
    await session.commit()


async def _create_and_store_tokens(
    session: AsyncSession,
    user_id: UUID,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[str, str]:
    """Create access + refresh tokens and store the refresh token in DB.

    Returns:
        Tuple of (access_token, refresh_token)
    """
    sub = str(user_id)
    access_token = create_access_token({"sub": sub})
    refresh_token = create_refresh_token({"sub": sub})
    token_hash = _hash_token(refresh_token)

    expire_time = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    db_refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expire_time,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    session.add(db_refresh_token)
    await session.commit()

    return access_token, refresh_token


async def _revoke_all_user_tokens(
    session: AsyncSession, user_id: UUID
) -> None:
    """Revoke ALL refresh tokens for a user (token reuse detection)."""
    statement = select(RefreshToken).where(
        (RefreshToken.user_id == user_id)
        & (RefreshToken.is_revoked == False)
    )
    result = await session.execute(statement)
    tokens = result.scalars().all()
    for token in tokens:
        token.is_revoked = True
        session.add(token)
    await session.commit()
    logger.warning("Revoked all tokens for user %s (possible reuse attack)", user_id)


async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[str, str]:
    """Register a new user and return tokens.

    Returns:
        Tuple of (access_token, refresh_token)

    Raises:
        HTTPException: If email already exists.
    """
    # Check if email already exists
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    existing_user = result.scalars().first()

    if existing_user:
        await _log_activity(
            session, None, "register_attempt",
            ip_address, user_agent, "failed - email already exists",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        email=email,
        password_hash=hash_password(password),
        role="user",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Log successful registration
    await _log_activity(
        session, user.id, "register",
        ip_address, user_agent, "success",
    )

    return await _create_and_store_tokens(
        session, user.id, ip_address, user_agent,
    )


async def login_user(
    session: AsyncSession,
    email: str,
    password: str,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[str, str]:
    """Authenticate a user and return tokens.

    Returns:
        Tuple of (access_token, refresh_token)

    Raises:
        HTTPException: If credentials are invalid or user is inactive.
    """
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user or not verify_password(password, user.password_hash):
        await _log_activity(
            session, None, "login_attempt",
            ip_address, user_agent, "failed - invalid credentials",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Rehash if Argon2 params have been upgraded
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
        session.add(user)
        await session.commit()
        logger.info("Rehashed password for user %s", user.id)

    if not user.is_active:
        await _log_activity(
            session, user.id, "login_attempt",
            ip_address, user_agent, "failed - user inactive",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    await _log_activity(
        session, user.id, "login",
        ip_address, user_agent, "success",
    )

    return await _create_and_store_tokens(
        session, user.id, ip_address, user_agent,
    )


async def refresh_tokens(
    session: AsyncSession,
    refresh_token: str,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[str, str]:
    """Refresh tokens using a valid refresh token (with rotation).

    Implements token reuse detection: if a revoked token is used,
    ALL tokens for that user are revoked as a security measure.

    Returns:
        Tuple of (new_access_token, new_refresh_token)
    """
    payload = decode_refresh_token(refresh_token)
    user_id_str = payload.get("sub")
    user_id = UUID(user_id_str)

    token_hash = _hash_token(refresh_token)
    statement = select(RefreshToken).where(
        (RefreshToken.user_id == user_id)
        & (RefreshToken.token_hash == token_hash)
        & (RefreshToken.is_revoked == False)
        & (RefreshToken.expires_at > datetime.now(timezone.utc))
    )
    result = await session.execute(statement)
    db_token = result.scalars().first()

    if not db_token:
        # Possible token reuse attack — revoke ALL tokens
        await _revoke_all_user_tokens(session, user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Revoke old token (rotation)
    db_token.is_revoked = True
    session.add(db_token)

    access_token, new_refresh_token = await _create_and_store_tokens(
        session, user_id, ip_address, user_agent,
    )

    await _log_activity(
        session, user_id, "token_refresh",
        ip_address, user_agent, "success",
    )

    return access_token, new_refresh_token


async def logout_user(
    session: AsyncSession,
    refresh_token: str,
    ip_address: str | None,
    user_agent: str | None,
) -> None:
    """Logout a user by revoking their refresh token."""
    try:
        payload = decode_refresh_token(refresh_token)
        user_id_str = payload.get("sub")
        user_id = UUID(user_id_str)

        token_hash = _hash_token(refresh_token)
        statement = select(RefreshToken).where(
            (RefreshToken.user_id == user_id)
            & (RefreshToken.token_hash == token_hash)
        )
        result = await session.execute(statement)
        db_token = result.scalars().first()

        if db_token:
            db_token.is_revoked = True
            session.add(db_token)
            await session.commit()

        await _log_activity(
            session, user_id, "logout",
            ip_address, user_agent, "success",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Logout error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )
