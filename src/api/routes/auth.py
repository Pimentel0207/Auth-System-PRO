from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib
from ...db.session import get_session
from ...models.models import User, RefreshToken, ActivityLog
from ...schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from ...core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_refresh_token
from ...core.config import settings


router = APIRouter()


def _hash_token(token: str) -> str:
    """Hash a token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


async def _log_activity(
    session: AsyncSession,
    user_id: str,
    action: str,
    ip_address: str | None,
    user_agent: str | None,
    activity_status: str
):
    """Log user activity."""
    log = ActivityLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        status=activity_status
    )
    session.add(log)
    await session.commit()


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user."""
    # Check if email already exists
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    existing_user = result.scalars().first()

    if existing_user:
        await _log_activity(
            session,
            str(uuid4()),
            "register_attempt",
            http_request.client.host if http_request.client else None,
            http_request.headers.get("user-agent"),
            "failed - email already exists"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role="user",
        is_active=True
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Log successful registration
    await _log_activity(
        session,
        str(user.id),
        "register",
        http_request.client.host if http_request.client else None,
        http_request.headers.get("user-agent"),
        "success"
    )

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    token_hash = _hash_token(refresh_token)

    # Store refresh token in database
    expire_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expira_em=expire_time,
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )

    session.add(db_refresh_token)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Login a user."""
    # Find user by email
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user or not verify_password(request.password, user.password_hash):
        await _log_activity(
            session,
            str(uuid4()),
            "login_attempt",
            http_request.client.host if http_request.client else None,
            http_request.headers.get("user-agent"),
            "failed - invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        await _log_activity(
            session,
            str(user.id),
            "login_attempt",
            http_request.client.host if http_request.client else None,
            http_request.headers.get("user-agent"),
            "failed - user inactive"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Log successful login
    await _log_activity(
        session,
        str(user.id),
        "login",
        http_request.client.host if http_request.client else None,
        http_request.headers.get("user-agent"),
        "success"
    )

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    token_hash = _hash_token(refresh_token)

    # Store refresh token in database
    expire_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expira_em=expire_time,
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )

    session.add(db_refresh_token)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Refresh access token using refresh token."""
    refresh_token = request.refresh_token

    # Validate refresh token
    payload = decode_refresh_token(refresh_token)
    user_id = payload.get("sub")

    # Check if token is in database and valid
    token_hash = _hash_token(refresh_token)
    statement = select(RefreshToken).where(
        (RefreshToken.user_id == user_id) &
        (RefreshToken.token_hash == token_hash) &
        (RefreshToken.revogado == False) &
        (RefreshToken.expira_em > datetime.now(timezone.utc))
    )

    result = await session.execute(statement)
    db_token = result.scalars().first()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Revoke old token
    db_token.revogado = True
    session.add(db_token)

    # Create new access token
    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id})
    new_token_hash = _hash_token(new_refresh_token)

    # Store new refresh token
    expire_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_token = RefreshToken(
        user_id=user_id,
        token_hash=new_token_hash,
        expira_em=expire_time,
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )

    session.add(new_db_token)
    await session.commit()

    # Log token refresh
    await _log_activity(
        session,
        user_id,
        "token_refresh",
        http_request.client.host if http_request.client else None,
        http_request.headers.get("user-agent"),
        "success"
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Logout a user by revoking their refresh token."""
    refresh_token = request.refresh_token

    try:
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")

        # Revoke the refresh token
        token_hash = _hash_token(refresh_token)
        statement = select(RefreshToken).where(
            (RefreshToken.user_id == user_id) &
            (RefreshToken.token_hash == token_hash)
        )

        result = await session.execute(statement)
        db_token = result.scalars().first()

        if db_token:
            db_token.revogado = True
            session.add(db_token)
            await session.commit()

        # Log logout
        await _log_activity(
            session,
            user_id,
            "logout",
            http_request.client.host if http_request.client else None,
            http_request.headers.get("user-agent"),
            "success"
        )

        return {"message": "Logged out successfully"}

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
