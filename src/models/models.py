from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone


class User(SQLModel, table=True):
    """User model — stores account credentials and metadata."""
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")
    password_reset_tokens: list["PasswordResetToken"] = Relationship(back_populates="user")
    activity_logs: list["ActivityLog"] = Relationship(back_populates="user")


class RefreshToken(SQLModel, table=True):
    """Refresh token model — stores hashed tokens for session management."""
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    token_hash: str
    is_revoked: bool = Field(default=False)
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="refresh_tokens")


class PasswordResetToken(SQLModel, table=True):
    """Password reset token model."""
    __tablename__ = "password_reset_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    token_hash: str
    is_used: bool = Field(default=False)
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="password_reset_tokens")


class ActivityLog(SQLModel, table=True):
    """Activity log model — audit trail for user actions."""
    __tablename__ = "activity_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID | None = Field(default=None, foreign_key="users.id")
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User | None = Relationship(back_populates="activity_logs")
