"""Database access layer for user operations."""
from uuid import UUID
from sqlalchemy import select, func, or_
from db_handler.database import db_manager
from models.db_models.enums import RoleLevel
from models.db_models.user import User


class UserDBHandler:
    """Handles user CRUD operations against the database."""

    @staticmethod
    def _normalize_phone(phone_number: str) -> str:
        """Normalize phone number for consistent DB lookups."""
        return "".join(ch for ch in phone_number if ch.isdigit())

    @staticmethod
    def _phone_match_clause(normalized_phone: str):
        """Build a SQL clause that matches raw or formatted stored phone values."""
        normalized_db_phone = func.regexp_replace(User.phone_number, r"\D", "", "g")
        clauses = [
            User.phone_number == normalized_phone,
            normalized_db_phone == normalized_phone,
        ]

        # Allow matching local 10-digit input with stored +country_code numbers.
        if len(normalized_phone) == 10:
            clauses.append(func.right(normalized_db_phone, 10) == normalized_phone)
 
        return or_(*clauses)

    @staticmethod
    async def get_by_email(email: str) -> User | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_password_by_email(email: str) -> str | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User.hashed_password).where(User.email == email))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(user_id: UUID) -> User | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_phone(phone_number: str) -> User | None:
        normalized_phone = UserDBHandler._normalize_phone(phone_number)
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(User).where(UserDBHandler._phone_match_clause(normalized_phone))
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def list_users(roles: list[RoleLevel] | None = None) -> list[User]:
        async with db_manager.session_factory() as db:
            stmt = select(User)
            if roles:
                stmt = stmt.where(User.role.in_(roles))

            result = await db.execute(stmt)
            return list(result.scalars().all())

    @staticmethod
    async def count_users(roles: list[RoleLevel] | None = None) -> int:
        async with db_manager.session_factory() as db:
            stmt = select(func.count()).select_from(User)
            if roles:
                stmt = stmt.where(User.role.in_(roles))
            return int(await db.scalar(stmt) or 0)

    @staticmethod
    async def list_users_paginated(page: int, page_size: int, roles: list[RoleLevel] | None = None) -> tuple[list[User], int]:
        offset = (page - 1) * page_size
        async with db_manager.session_factory() as db:
            stmt = select(User)
            count_stmt = select(func.count()).select_from(User)
            if roles:
                stmt = stmt.where(User.role.in_(roles))
                count_stmt = count_stmt.where(User.role.in_(roles))

            total = int(await db.scalar(count_stmt) or 0)
            result = await db.execute(stmt.order_by(User.created_at.desc()).offset(offset).limit(page_size))
            return list(result.scalars().all()), total

    @staticmethod
    async def create(user: User) -> User:
        user.phone_number = UserDBHandler._normalize_phone(user.phone_number)
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

            if "phone_number" in update_data and update_data["phone_number"] is not None:
                update_data["phone_number"] = UserDBHandler._normalize_phone(update_data["phone_number"])

            for field, value in update_data.items():
                setattr(user, field, value)

            await db.commit()
            await db.refresh(user)
            return user

    @staticmethod
    async def update_by_phone(phone_number: str, update_data: dict) -> User | None:
        normalized_phone = UserDBHandler._normalize_phone(phone_number)
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(User).where(UserDBHandler._phone_match_clause(normalized_phone))
            )
            user = result.scalar_one_or_none()
            if user is None:
                return None

            if "phone_number" in update_data and update_data["phone_number"] is not None:
                update_data["phone_number"] = UserDBHandler._normalize_phone(update_data["phone_number"])

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

    @staticmethod
    async def delete_by_phone(phone_number: str) -> bool:
        normalized_phone = UserDBHandler._normalize_phone(phone_number)
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(User).where(UserDBHandler._phone_match_clause(normalized_phone))
            )
            user = result.scalar_one_or_none()
            if user is None:
                return False

            await db.delete(user)
            await db.commit()
            return True
