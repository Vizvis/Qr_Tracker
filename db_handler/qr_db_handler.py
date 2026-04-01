"""Database access layer for QR Code operations."""
from uuid import UUID
from datetime import datetime
from sqlalchemy import delete, select
from db_handler.database import db_manager
from models.db_models.produced_items import ProducedItems
from models.db_models.qr_code import QRCode
from models.db_models.remarks import Remarks


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

    @staticmethod
    async def finish_session(qr_id: str) -> int:
        """Move all remarks for a QR into produced_items and clear source remarks."""
        async with db_manager.session_factory() as db:
            remarks = (
                await db.scalars(
                    select(Remarks)
                    .where(Remarks.qr_id == qr_id)
                    .order_by(Remarks.created_at.asc())
                )
            ).all()

            if not remarks:
                return 0

            for remark in remarks:
                if remark.department_id is None:
                    raise ValueError("Department is required for all remarks before finishing session.")

                produced_item = ProducedItems(
                    qr_id=qr_id,
                    item_id=remark.item_id,
                    department_id=remark.department_id,
                    general_remarks=remark.general_remarks,
                    issue_remarks=remark.issue_remarks,
                    created_at=remark.created_at,
                )
                db.add(produced_item)

            await db.execute(delete(Remarks).where(Remarks.qr_id == qr_id))
            await db.commit()
            return len(remarks)

