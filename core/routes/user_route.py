"""User API routes (router/blueprint) for auth and CRUD operations."""
from uuid import UUID
from fastapi import APIRouter, Response, status
from auth.cookie_auth import CookieAuth
from core.services.user_service import UserService
from models.api_models.user_models import (
    UserCreateRequest,
    UserUpdateRequest,
    UserLoginRequest,
    UserResponse,
    AuthResponse,
    MessageResponse,
)


user_router = APIRouter(prefix="/api/users", tags=["Users"])


@user_router.post("/login", response_model=AuthResponse)
async def login(payload: UserLoginRequest, response: Response):
    """Login endpoint and set access token cookie."""
    access_token, user = await UserService.login_user(payload)
    CookieAuth.set_auth_cookie(response, access_token)

    return AuthResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user.id),
            name=user.name,
            phone_number=user.phone_number,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        ),
    )


@user_router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    """Logout endpoint and clear auth cookies."""
    CookieAuth.delete_auth_cookies(response)
    return MessageResponse(message="Logged out successfully.")


@user_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreateRequest):
    """Create user endpoint."""
    user = await UserService.create_user(payload)
    return UserResponse(
        id=str(user.id),
        name=user.name,
        phone_number=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@user_router.put("/phone/{phone_number}", response_model=UserResponse)
async def modify_user(phone_number: str, payload: UserUpdateRequest):
    """Modify user endpoint."""
    user = await UserService.update_user_by_phone(phone_number, payload)
    return UserResponse(
        id=str(user.id),
        name=user.name,
        phone_number=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@user_router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: UUID):
    """Delete user endpoint."""
    await UserService.delete_user(user_id)
    return MessageResponse(message="User deleted successfully.")
