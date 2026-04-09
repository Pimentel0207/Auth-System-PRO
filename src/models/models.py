from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")
    password_reset_tokens: list["PasswordResetToken"] = Relationship(back_populates="user")
    activity_logs: list["ActivityLog"] = Relationship(back_populates="user")


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    token_hash: str
    revogado: bool = Field(default=False)
    expira_em: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="refresh_tokens")


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_token"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    token_hash: str
    usado: bool = Field(default=False)
    expira_em: datetime
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="password_reset_tokens")


class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="activity_logs")
