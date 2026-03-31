"""Pydantic API models for user endpoints."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from models.db_models.enums import RoleLevel


class UserCreateRequest(BaseModel):
    """Request body for creating a user."""

    name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=7, max_length=20)
    email: str
    password: str = Field(min_length=6, max_length=72)
    role: RoleLevel


class UserUpdateRequest(BaseModel):
    """Request body for updating a user."""

    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone_number: str | None = Field(default=None, min_length=7, max_length=20)
    email: str | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)
    role: RoleLevel | None = None
    is_active: bool | None = None


class UserLoginRequest(BaseModel):
    """Request body for login endpoint."""

    email: str
    password: str = Field(min_length=6, max_length=72)


class UserResponse(BaseModel):
    """Public user response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    phone_number: str
    email: str
    role: RoleLevel
    is_active: bool
    created_at: datetime


class AuthResponse(BaseModel):
    """Authentication response payload."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Simple message response payload."""

    message: str
