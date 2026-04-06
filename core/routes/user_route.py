"""User API routes (router/blueprint) for auth and CRUD operations."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from auth.cookie_auth import CookieAuth, require_valid_auth_cookie
from auth.dependencies import get_current_user_token, require_role
from core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from core.services.user_service import UserService
from models.db_models.enums import RoleLevel
from models.api_models.user_models import (
    UserCreateRequest,
    UserUpdateRequest,
    UserLoginRequest,
    UserResponse,
    AuthResponse,
    MessageResponse,
    ChangePasswordRequest,
    AdminPasswordResetRequest,
    UserListResponse,
)

user_router = APIRouter(prefix="/api/users", tags=["Users"])


@user_router.get("", response_model=UserListResponse)
async def get_users(
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    roles: Annotated[
        list[str] | None,
        Query(description="Optional role filters. Supports repeated params or comma-separated values."),
    ] = None,
):
    """Get all users, or only users matching provided roles."""
    parsed_roles: list[RoleLevel] | None = None
    if roles:
        tokens = [part.strip().lower() for value in roles for part in value.split(",") if part.strip()]
        invalid_roles = [token for token in tokens if token not in {role.value for role in RoleLevel}]
        if invalid_roles:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid roles: {', '.join(invalid_roles)}",
            )
        parsed_roles = [RoleLevel(token) for token in tokens]

    return await UserService.get_users(page, page_size, parsed_roles)


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
async def logout(
    response: Response,
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Logout endpoint and clear auth cookies."""
    CookieAuth.delete_auth_cookies(response)
    return MessageResponse(message="Logged out successfully.")


@user_router.put("/me/password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Change logged-in user's password."""
    user_id = UUID(current_user["user_id"])
    await UserService.change_password(user_id, payload)
    return MessageResponse(message="Password updated successfully.")


@user_router.put("/{user_id}/reset-password", response_model=MessageResponse)
async def admin_reset_password(
    user_id: Annotated[UUID, Path(..., description="User ID")],
    payload: AdminPasswordResetRequest,
    current_user: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Admin endpoint to arbitrarily change a user's password."""
    role_str = str(current_user.get("role", "")).lower()
    if role_str != "admin" and role_str != "rolelevel.admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required.",
        )
    
    await UserService.admin_reset_password(user_id, payload)
    return MessageResponse(message="User password reset successfully.")


@user_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    # _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
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
async def modify_user(
    phone_number: Annotated[
        str,
        Path(
            ...,
            min_length=10,
            max_length=10,
            pattern=r"^\d{10}$",
            description="Phone number must be exactly 10 digits.",
        ),
    ],
    payload: UserUpdateRequest,
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
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


@user_router.delete("/phone/{phone_number}", response_model=MessageResponse)
async def delete_user(
    phone_number: Annotated[
        str,
        Path(
            ...,
            min_length=10,
            max_length=10,
            pattern=r"^\d{10}$",
            description="Phone number must be exactly 10 digits.",
        ),
    ],
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Delete user endpoint."""
    await UserService.delete_user_by_phone(phone_number)
    return MessageResponse(message="User deleted successfully.")


@user_router.get("/me", response_model=UserResponse)
async def get_me(
    payload: Annotated[dict, Depends(get_current_user_token)],
):
    """Get the currently authenticated user profile from auth cookie token."""
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    try:
        user_uuid = UUID(str(user_id))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        ) from exc

    user = await UserService.get_user_by_id(user_uuid)
    return UserResponse(
        id=str(user.id),
        name=user.name,
        phone_number=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: Annotated[UUID, Path(..., description="User ID")],
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Get user by ID endpoint."""
    user = await UserService.get_user_by_id(user_id)
    return UserResponse(
        id=str(user.id),
        name=user.name,
        phone_number=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@user_router.delete("/{id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_user_by_id(
    id: Annotated[UUID, Path(..., description="The ID of the user to delete")],
    current_user_id: UUID = Depends(require_role(["admin"]))
):
    """Delete a user from the system by ID (Admin only)."""
    await UserService.delete_user_by_id(id)
    return {"detail": "User successfully deleted"}
