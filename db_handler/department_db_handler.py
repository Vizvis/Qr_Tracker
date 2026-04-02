"""Database access layer for department operations."""
from uuid import UUID
from sqlalchemy import func, select
from db_handler.database import db_manager
from models.db_models.department import Department


class DepartmentDBHandler:
    """Handles department CRUD operations against the database."""

    @staticmethod
    async def list_all() -> list[Department]:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(Department))
            return list(result.scalars().all())

    @staticmethod
    async def count_all() -> int:
        async with db_manager.session_factory() as db:
            return int(await db.scalar(select(func.count()).select_from(Department)) or 0)

    @staticmethod
    async def list_paginated(page: int, page_size: int) -> tuple[list[Department], int]:
        offset = (page - 1) * page_size
        async with db_manager.session_factory() as db:
            total = int(await db.scalar(select(func.count()).select_from(Department)) or 0)
            result = await db.execute(
                select(Department)
                .order_by(Department.created_on.desc())
                .offset(offset)
                .limit(page_size)
            )
            return list(result.scalars().all()), total

    @staticmethod
    async def get_by_id(department_id: UUID) -> Department | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(Department).where(Department.id == department_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def create(department: Department) -> Department:
        async with db_manager.session_factory() as db:
            db.add(department)
            await db.commit()
            await db.refresh(department)
            return department

    @staticmethod
    async def update(department_id: UUID, update_data: dict) -> Department | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(Department).where(Department.id == department_id))
            department = result.scalar_one_or_none()
            if department is None:
                return None

            for field, value in update_data.items():
                setattr(department, field, value)

            await db.commit()
            await db.refresh(department)
            return department
