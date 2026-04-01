"""Database access layer for department operations."""
from uuid import UUID
from sqlalchemy import select
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
