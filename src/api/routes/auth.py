"""
Auth routes — thin HTTP layer that delegates to auth_service.

Rate-limited endpoints:
  - /register: 3 requests/minute per IP
  - /login: 5 requests/minute per IP
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.rate_limit import limiter
from ...db.session import get_session
from ...schemas.schemas import (
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from ...services import auth_service
from ...core.config import settings


router = APIRouter()


def _get_client_info(request: Request) -> tuple[str | None, str | None]:
    """Extract IP address and user-agent from request."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    return ip, ua


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new user",
    responses={409: {"description": "Email already registered"}},
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user and return access + refresh tokens."""
    ip, ua = _get_client_info(request)
    access_token, refresh_token = await auth_service.register_user(
        session, data.email, data.password, ip, ua,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with credentials",
    responses={
        401: {"description": "Invalid credentials"},
        403: {"description": "User inactive"},
    },
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate a user and return access + refresh tokens."""
    ip, ua = _get_client_info(request)
    access_token, refresh_token = await auth_service.login_user(
        session, data.email, data.password, ip, ua,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    responses={401: {"description": "Invalid or expired refresh token"}},
)
async def refresh(
    request: Request,
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
):
    """Refresh tokens using a valid refresh token (with rotation)."""
    ip, ua = _get_client_info(request)
    access_token, new_refresh_token = await auth_service.refresh_tokens(
        session, data.refresh_token, ip, ua,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (revoke refresh token)",
)
async def logout(
    request: Request,
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
):
    """Logout a user by revoking their refresh token."""
    ip, ua = _get_client_info(request)
    await auth_service.logout_user(session, data.refresh_token, ip, ua)
    return MessageResponse(message="Logged out successfully")
