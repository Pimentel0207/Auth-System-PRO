from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime


def _check_password_strength(password: str) -> str:
    """Enforce password complexity rules."""
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")
    return password


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def check_strength(cls, v: str) -> str:
        return _check_password_strength(v)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


class TokenResponse(BaseModel):
    """Schema for token response — now includes refresh_token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def check_strength(cls, v: str) -> str:
        return _check_password_strength(v)


class UserUpdateRequest(BaseModel):
    """Schema for user profile update."""
    email: EmailStr | None = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "role": "user",
                "is_active": True,
                "created_at": "2024-04-10T10:00:00Z",
                "updated_at": "2024-04-10T10:00:00Z"
            }
        }
    }


class UserStatusRequest(BaseModel):
    """Schema for toggling user active status (admin)."""
    is_active: bool


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Invalid credentials"
            }
        }
    }
