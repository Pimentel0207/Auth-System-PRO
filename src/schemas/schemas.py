from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "role": "user",
                "is_active": True,
                "created_at": "2024-04-10T10:00:00Z"
            }
        }


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ErrorResponse(BaseModel):
    detail: str
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials",
                "status_code": 401
            }
        }
