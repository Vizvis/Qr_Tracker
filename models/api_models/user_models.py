"""Pydantic API models for user endpoints."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from models.db_models.enums import RoleLevel


class UserCreateRequest(BaseModel):
    """Request body for creating a user."""

    name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    role: RoleLevel


class UserUpdateRequest(BaseModel):
    """Request body for updating a user."""

    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone_number: str | None = Field(default=None, min_length=10, max_length=10, pattern=r"^\d{10}$")
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)
    role: RoleLevel | None = None
    is_active: bool | None = None


class UserLoginRequest(BaseModel):
    """Request body for login endpoint."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class ChangePasswordRequest(BaseModel):
    """Request body for changing password."""

    current_password: str
    new_password: str = Field(min_length=6, max_length=72)


class AdminPasswordResetRequest(BaseModel):
    """Request body for admin password reset."""

    new_password: str = Field(min_length=6, max_length=72)


class UserResponse(BaseModel):
    """Public user response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    phone_number: str
    email: EmailStr
    role: int
    is_active: bool
    created_at: datetime

    @field_validator("role", mode="before")
    @classmethod
    def serialize_role(cls, v):
        val = v.value if hasattr(v, "value") else str(v)
        role_map = {
            "admin": 3,
            "supervisor": 2,
            "operator": 1,
            "viewer": 0,
        }
        return role_map.get(val, 0)


class AuthResponse(BaseModel):
    """Authentication response payload."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Simple message response payload."""

    message: str
