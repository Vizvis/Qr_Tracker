"""Database access layer for QR Code operations."""
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from db_handler.database import db_manager
from models.db_models.qr_code import QRCode


class QRDBHandler:
    """Handles QR Code CRUD operations against the database."""

    @staticmethod
    async def get_by_id(qr_id: str) -> QRCode | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(QRCode).where(QRCode.id == qr_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_all() -> list[QRCode]:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(QRCode))
            return list(result.scalars().all())

    @staticmethod
    async def create(qr_code: QRCode) -> QRCode:
        async with db_manager.session_factory() as db:
            db.add(qr_code)
            await db.commit()
            await db.refresh(qr_code)
            return qr_code

    @staticmethod
    async def update_status(qr_id: str, new_status: str, action_by: UUID, notes: str | None = None) -> QRCode | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(QRCode).where(QRCode.id == qr_id))
            qr_code = result.scalar_one_or_none()
            if qr_code is None:
                return None

            qr_code.status = new_status
            if notes is not None:
                 qr_code.notes = notes

            if new_status == "active":
                qr_code.enabled_by = action_by
                qr_code.enabled_at = datetime.utcnow()
            elif new_status == "inactive":
                qr_code.enabled_by = None
                qr_code.enabled_at = None

            await db.commit()
            await db.refresh(qr_code)
            return qr_code

