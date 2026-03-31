"""Database access layer for user operations."""
from uuid import UUID
from sqlalchemy import select
from db_handler.database import db_manager
from models.db_models.user import User


class UserDBHandler:
    """Handles user CRUD operations against the database."""

    @staticmethod
    async def get_by_email(email: str) -> User | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(user_id: UUID) -> User | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_phone(phone_number: str) -> User | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            return result.scalar_one_or_none()

    @staticmethod
    async def create(user: User) -> User:
        async with db_manager.session_factory() as db:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

    @staticmethod
    async def update(user_id: UUID, update_data: dict) -> User | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                return None

            for field, value in update_data.items():
                setattr(user, field, value)

            await db.commit()
            await db.refresh(user)
            return user

    @staticmethod
    async def update_by_phone(phone_number: str, update_data: dict) -> User | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalar_one_or_none()
            if user is None:
                return None

            for field, value in update_data.items():
                setattr(user, field, value)

            await db.commit()
            await db.refresh(user)
            return user

    @staticmethod
    async def delete(user_id: UUID) -> bool:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                return False

            await db.delete(user)
            await db.commit()
            return True
