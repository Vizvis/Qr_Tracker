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
            result = await db.execute(select(Department).order_by(Department.sequence_order.asc()))
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
                .order_by(Department.sequence_order.asc())
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
    async def name_exists(name: str, exclude_department_id: UUID | None = None) -> bool:
        async with db_manager.session_factory() as db:
            stmt = select(Department.id).where(Department.name == name)
            if exclude_department_id is not None:
                stmt = stmt.where(Department.id != exclude_department_id)
            result = await db.execute(stmt.limit(1))
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def sequence_order_exists(sequence_order: int, exclude_department_id: UUID | None = None) -> bool:
        async with db_manager.session_factory() as db:
            stmt = select(Department.id).where(Department.sequence_order == sequence_order)
            if exclude_department_id is not None:
                stmt = stmt.where(Department.id != exclude_department_id)
            result = await db.execute(stmt.limit(1))
            return result.scalar_one_or_none() is not None

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

    @staticmethod
    async def delete(department_id: UUID) -> bool:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(Department).where(Department.id == department_id))
            department = result.scalar_one_or_none()
            if department is None:
                return False
                
            await db.delete(department)
            await db.commit()
            return True
