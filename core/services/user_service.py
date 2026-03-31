"""User service layer for business logic and auth workflows."""
from fastapi import HTTPException, status
from auth.jwt_auth import JWTAuth
from db_handler.user_db_handler import UserDBHandler
from models.db_models.user import User
from models.api_models.user_models import UserCreateRequest, UserUpdateRequest, UserLoginRequest


class UserService:
    """Business logic for user and auth endpoints."""

    @staticmethod
    async def create_user(payload: UserCreateRequest) -> User:
        existing_user = await UserDBHandler.get_by_email(payload.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        existing_phone = await UserDBHandler.get_by_phone(payload.phone_number)
        if existing_phone is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this phone number already exists.",
            )

        new_user = User(
            name=payload.name,
            phone_number=payload.phone_number,
            email=payload.email,
            hashed_password=JWTAuth.hash_password(payload.password),
            role=payload.role,
        )
        return await UserDBHandler.create(new_user)

    @staticmethod
    async def login_user(payload: UserLoginRequest) -> tuple[str, User]:
        user = await UserDBHandler.get_by_email(payload.email)
        if user is None or not JWTAuth.verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        try:
            access_token = JWTAuth.create_access_token(
                {
                    "sub": user.email,
                    "user_id": str(user.id),
                    "role": str(user.role),
                }
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc

        return access_token, user

    @staticmethod
    async def update_user_by_phone(phone_number: str, payload: UserUpdateRequest) -> User:
        user = await UserDBHandler.get_by_phone(phone_number)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if payload.email and payload.email != user.email:
            existing_user = await UserDBHandler.get_by_email(payload.email)
            if existing_user is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another user with this email already exists.",
                )

        if payload.phone_number and payload.phone_number != user.phone_number:
            existing_phone = await UserDBHandler.get_by_phone(payload.phone_number)
            if existing_phone is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another user with this phone number already exists.",
                )

        update_data = {}
        if payload.email is not None:
            update_data["email"] = payload.email
        if payload.phone_number is not None:
            update_data["phone_number"] = payload.phone_number
        if payload.name is not None:
            update_data["name"] = payload.name
        if payload.password is not None:
            update_data["hashed_password"] = JWTAuth.hash_password(payload.password)
        if payload.role is not None:
            update_data["role"] = payload.role
        if payload.is_active is not None:
            update_data["is_active"] = payload.is_active

        updated_user = await UserDBHandler.update_by_phone(phone_number, update_data)
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return updated_user

    @staticmethod
    async def delete_user_by_phone(phone_number: str) -> None:
        deleted = await UserDBHandler.delete_by_phone(phone_number)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
