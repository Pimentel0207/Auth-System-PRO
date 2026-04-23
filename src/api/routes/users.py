"""
User routes — profile management and admin operations.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.dependencies import get_current_user, require_admin
from ...db.session import get_session
from ...models.models import User
from ...schemas.schemas import (
    MessageResponse,
    PasswordChangeRequest,
    UserResponse,
    UserStatusRequest,
    UserUpdateRequest,
)
from ...services import user_service


router = APIRouter()


# ─── Authenticated User Routes ────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get information about the currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_me(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update the current user's profile (email)."""
    if request.email:
        current_user = await user_service.update_user_email(
            session, current_user, request.email
        )
    return UserResponse.model_validate(current_user)


@router.put(
    "/me/password",
    response_model=MessageResponse,
    summary="Change password",
)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Change the current user's password."""
    await user_service.change_password(
        session, current_user, request.current_password, request.new_password
    )
    return MessageResponse(message="Password changed successfully")


# ─── Admin Routes ─────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all users (admin)",
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """List all users. Requires admin role."""
    users = await user_service.list_users(session, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.put(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Activate/deactivate user (admin)",
)
async def toggle_user_status(
    user_id: UUID,
    request: UserStatusRequest,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Activate or deactivate a user. Requires admin role."""
    user = await user_service.toggle_user_status(
        session, user_id, request.is_active
    )
    return UserResponse.model_validate(user)
