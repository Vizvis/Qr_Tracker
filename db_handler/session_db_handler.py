"""Database access layer for session-style remarks lookups."""
from uuid import UUID

from sqlalchemy import String as SQLString, cast, desc, select
from db_handler.database import db_manager
from models.db_models.department import Department
from models.db_models.qr_code import QRCode
from models.db_models.remarks import Remarks


class SessionDBHandler:
    """Handles remark retrieval by qr_id for session endpoints."""

    @staticmethod
    async def create_remark(
        qr_id: str,
        item_id: str,
        department_id: UUID,
        general_remarks: str | None,
        issue_remarks: str | None,
    ) -> tuple[Remarks, str | None]:
        async with db_manager.session_factory() as db:
            remark = Remarks(
                qr_id=qr_id,
                item_id=item_id,
                department_id=department_id,
                general_remarks=general_remarks,
                issue_remarks=issue_remarks,
            )
            db.add(remark)
            await db.commit()
            await db.refresh(remark)

            result = await db.execute(
                select(Department.dept_type)
                .where(Department.id == department_id)
                .limit(1)
            )
            dept_type = result.scalar_one_or_none()
            return (remark, dept_type.value if dept_type is not None else None)

    @staticmethod
    async def has_department_update(qr_id: str, department_id: UUID) -> bool:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(Remarks.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .where(Remarks.department_id == department_id)
                .limit(1)
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def has_item_department_update(qr_id: str, item_id: str, department_id: UUID) -> bool:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(Remarks.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .where(Remarks.item_id == item_id)
                .where(Remarks.department_id == department_id)
                .limit(1)
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def list_remarks_by_qr_id(qr_id: str) -> list[tuple[Remarks, str | None]]:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(Remarks, Department.dept_type)
                .outerjoin(Department, Remarks.department_id == Department.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .order_by(Remarks.created_at.asc())
            )
            rows = result.all()
            return [
                (remark, dept_type.value if dept_type is not None else None)
                for remark, dept_type in rows
            ]

    @staticmethod
    async def get_latest_remark_by_qr_id(qr_id: str) -> tuple[Remarks, str | None] | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(Remarks, Department.dept_type)
                .outerjoin(Department, Remarks.department_id == Department.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .order_by(desc(Remarks.created_at))
                .limit(1)
            )
            row = result.first()
            if row is None:
                return None

            remark, dept_type = row
            return (remark, dept_type.value if dept_type is not None else None)

    @staticmethod
    async def list_active_qr_remarks() -> list[dict]:
        async with db_manager.session_factory() as db:
            active_qrs = (
                await db.scalars(
                    select(QRCode)
                    .where(QRCode.status == "active")
                    .order_by(QRCode.enabled_at.desc(), QRCode.id.asc())
                )
            ).all()

            if not active_qrs:
                return []

            qr_ids = [qr.id for qr in active_qrs]
            rows = (
                await db.execute(
                    select(Remarks, Department.dept_type)
                    .outerjoin(Department, Remarks.department_id == Department.id)
                    .where(Remarks.qr_id.in_(qr_ids))
                    .order_by(Remarks.created_at.asc())
                )
            ).all()

            remarks_by_qr: dict[str, list[dict]] = {qr_id: [] for qr_id in qr_ids}
            for remark, dept_type in rows:
                remarks_by_qr.setdefault(str(remark.qr_id), []).append(
                    {
                        "id": str(remark.id),
                        "qr_id": str(remark.qr_id),
                        "item_id": remark.item_id,
                        "department_id": str(remark.department_id) if remark.department_id else None,
                        "department": dept_type.value if dept_type is not None else None,
                        "general_remarks": remark.general_remarks,
                        "issue_remarks": remark.issue_remarks,
                        "created_at": remark.created_at,
                    }
                )

            return [
                {
                    "qr_id": qr.id,
                    "status": qr.status,
                    "enabled_at": qr.enabled_at,
                    "notes": qr.notes,
                    "remarks": remarks_by_qr.get(qr.id, []),
                }
                for qr in active_qrs
            ]
