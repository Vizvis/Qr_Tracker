"""Database access layer for session-style remarks lookups."""
import logging
from uuid import UUID

from sqlalchemy import String as SQLString, cast, delete, desc, func, select
from sqlalchemy.exc import IntegrityError
from db_handler.database import db_manager
from models.db_models.department import Department
from models.db_models.qr_code import QRCode
from models.db_models.produced_items import ProducedItems
from models.db_models.remarks import Remarks

from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SessionDBHandler:
    """Handles remark retrieval by qr_id for session endpoints."""

    @staticmethod
    async def is_item_id_used_by_other_qr(item_id: str, current_qr_id: str) -> bool:
        async with db_manager.session_factory() as db:
            remark = await db.scalar(
                select(Remarks).where(
                    Remarks.item_id == item_id,
                    Remarks.qr_id != current_qr_id
                ).limit(1)
            )
            if remark:
                return True
            
            produced = await db.scalar(
                select(ProducedItems).where(
                    ProducedItems.item_id == item_id,
                    ProducedItems.qr_id != current_qr_id
                ).limit(1)
            )
            if produced:
                return True
            
            return False

    @staticmethod
    async def create_remark(
        qr_id: str,
        item_id: str,
        department_id: UUID,
        field_1: int | None,
        field_2: int | None,
        field_3: int | None,
        field_4: int | None,
        field_5: int | None,
        issue_remarks: str | None,
        custom_data: dict | None = None,
        current_user_id: UUID | None = None,
    ) -> tuple[Remarks, str | None]:
        async with db_manager.session_factory() as db:
            remark = Remarks(
                qr_id=qr_id,
                item_id=item_id,
                department_id=department_id,
                field_1=field_1 if field_1 is not None else 0,
                field_2=field_2 if field_2 is not None else 0,
                field_3=field_3 if field_3 is not None else 0,
                field_4=field_4 if field_4 is not None else 0,
                field_5=field_5 if field_5 is not None else 0,
                issue_remarks=issue_remarks,
                custom_data=custom_data if custom_data is not None else {},
                remark_by=current_user_id,
                remark_updated=current_user_id,
            )
            db.add(remark)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                raise
            await db.refresh(remark)

            result = await db.execute(
                select(Department.name)
                .where(Department.id == department_id)
                .limit(1)
            )
            dept_name = result.scalar_one_or_none()
            return (remark, dept_name if dept_name is not None else None)

    @staticmethod
    async def get_by_id(remark_id: UUID) -> Remarks | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(Remarks).where(Remarks.id == remark_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def list_all_remarks(page: int, page_size: int) -> tuple[list[tuple[Remarks, str | None]], int]:
        offset = (page - 1) * page_size
        async with db_manager.session_factory() as db:
            total = await db.scalar(select(func.count()).select_from(Remarks))
            result = await db.execute(
                select(Remarks, Department.name)
                .outerjoin(Department, Remarks.department_id == Department.id)
                .order_by(Remarks.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            rows = result.all()
            return [
                (remark, dept_name if dept_name is not None else None)
                for remark, dept_name in rows
            ], int(total or 0)

    @staticmethod
    async def update_remark(
        remark_id: UUID,
        update_data: dict,
        current_user_id: UUID | None = None,
    ) -> tuple[Remarks, str | None] | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(select(Remarks).where(Remarks.id == remark_id))
            remark = result.scalar_one_or_none()
            if remark is None:
                return None

            # Append current state to history
            history_entry = {
                "date": remark.updated_at.isoformat() if getattr(remark, 'updated_at', None) else remark.created_at.isoformat(),
                "field_1": remark.field_1,
                "field_2": remark.field_2,
                "field_3": remark.field_3,
                "field_4": remark.field_4,
                "field_5": remark.field_5,
                "issue_remarks": remark.issue_remarks
            }
            
            # Using simple list manipulation since JSONB is returned as a list
            current_history = list(remark.remarks_history) if remark.remarks_history else []
            current_history.append(history_entry)
            remark.remarks_history = current_history

            # Apply new updates
            for field, value in update_data.items():
                setattr(remark, field, value)

            if current_user_id is not None:
                remark.remark_updated = current_user_id

            # updated_at must be timezone-naive to match the DB column
            remark.updated_at = datetime.utcnow()

            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                raise
            await db.refresh(remark)

            result = await db.execute(
                select(Department.name)
                .where(Department.id == remark.department_id)
                .limit(1)
            )
            dept_name = result.scalar_one_or_none()
            return (remark, dept_name if dept_name is not None else None)

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
                select(Remarks, Department.name)
                .outerjoin(Department, Remarks.department_id == Department.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .order_by(Remarks.created_at.asc())
            )
            rows = result.all()
            return [
                (remark, dept_name if dept_name is not None else None)
                for remark, dept_name in rows
            ]

    @staticmethod
    async def get_latest_remark_by_qr_id(qr_id: str) -> tuple[Remarks, str | None] | None:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(Remarks, Department.name)
                .outerjoin(Department, Remarks.department_id == Department.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .order_by(desc(Remarks.created_at))
                .limit(1)
            )
            row = result.first()
            if row is None:
                return None

            remark, dept_name = row
            return (remark, dept_name if dept_name is not None else None)

    @staticmethod
    async def get_previous_department_remark(qr_id: str, item_id: str, department_id: UUID) -> Remarks | None:
        """Get the remark from the previous department (lower sequence_order) for cascade validation."""
        async with db_manager.session_factory() as db:
            # Get the sequence_order of the current department
            current_dept = await db.execute(
                select(Department.sequence_order)
                .where(Department.id == department_id)
                .limit(1)
            )
            current_seq = current_dept.scalar_one_or_none()
            if current_seq is None:
                return None

            # Find the remark from the department with the next-lower sequence_order
            result = await db.execute(
                select(Remarks)
                .join(Department, Remarks.department_id == Department.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .where(Remarks.item_id == item_id)
                .where(Department.sequence_order < current_seq)
                .order_by(desc(Department.sequence_order))
                .limit(1)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_all_previous_department_remarks(qr_id: str, item_id: str, department_id: UUID) -> list[Remarks]:
        """Get all remarks from previous departments (lower sequence_order), ordered by descending sequence."""
        async with db_manager.session_factory() as db:
            current_dept = await db.execute(
                select(Department.sequence_order)
                .where(Department.id == department_id)
                .limit(1)
            )
            current_seq = current_dept.scalar_one_or_none()
            if current_seq is None:
                return []

            result = await db.execute(
                select(Remarks)
                .join(Department, Remarks.department_id == Department.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .where(Remarks.item_id == item_id)
                .where(Department.sequence_order < current_seq)
                .order_by(desc(Department.sequence_order))
            )
            return list(result.scalars().all())

    @staticmethod
    async def has_subsequent_department_remark(qr_id: str, item_id: str, department_id: UUID) -> bool:
        """Check if any department with a higher sequence_order has already logged data."""
        async with db_manager.session_factory() as db:
            # Get current department's sequence_order
            current_dept = await db.execute(
                select(Department.sequence_order)
                .where(Department.id == department_id)
                .limit(1)
            )
            current_seq = current_dept.scalar_one_or_none()
            if current_seq is None:
                return False

            result = await db.execute(
                select(Remarks.id)
                .join(Department, Remarks.department_id == Department.id)
                .where(cast(Remarks.qr_id, SQLString) == qr_id)
                .where(Remarks.item_id == item_id)
                .where(Department.sequence_order > current_seq)
                .limit(1)
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def list_active_qr_remarks(page: int, page_size: int) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        async with db_manager.session_factory() as db:
            total = await db.scalar(
                select(func.count()).select_from(QRCode).where(QRCode.status == "active")
            )
            active_qrs = (
                await db.scalars(
                    select(QRCode)
                    .where(QRCode.status == "active")
                    .order_by(QRCode.enabled_at.desc(), QRCode.id.asc())
                    .offset(offset)
                    .limit(page_size)
                )
            ).all()

            if not active_qrs:
                return [], int(total or 0)

            qr_ids = [qr.id for qr in active_qrs]
            rows = (
                await db.execute(
                    select(Remarks, Department.name)
                    .outerjoin(Department, Remarks.department_id == Department.id)
                    .where(Remarks.qr_id.in_(qr_ids))
                    .order_by(Remarks.created_at.asc())
                )
            ).all()

            remarks_by_qr: dict[str, list[dict]] = {qr_id: [] for qr_id in qr_ids}
            for remark, dept_name in rows:
                remarks_by_qr.setdefault(str(remark.qr_id), []).append(
                    {
                        "id": str(remark.id),
                        "qr_id": str(remark.qr_id),
                        "item_id": remark.item_id,
                        "department_id": str(remark.department_id) if remark.department_id else None,
                        "department": dept_name if dept_name is not None else None,
                        "field_1": remark.field_1 if remark.field_1 is not None else 0,
                        "field_2": remark.field_2 if remark.field_2 is not None else 0,
                        "field_3": remark.field_3 if remark.field_3 is not None else 0,
                        "field_4": remark.field_4 if remark.field_4 is not None else 0,
                        "field_5": remark.field_5 if remark.field_5 is not None else 0,
                        "issue_remarks": remark.issue_remarks,
                        "remarks_history": remark.remarks_history if remark.remarks_history is not None else [],
                        "remark_by": str(remark.remark_by) if remark.remark_by else None,
                        "remark_updated": str(remark.remark_updated) if getattr(remark, 'remark_updated', None) else None,
                        "created_at": remark.created_at.replace(tzinfo=timezone.utc) if remark.created_at else None,
                        "updated_at": remark.updated_at.replace(tzinfo=timezone.utc) if getattr(remark, 'updated_at', None) else None,
                    }
                )

            return [
                {
                    "qr_id": qr.id,
                    "status": qr.status,
                    "enabled_at": qr.enabled_at.replace(tzinfo=timezone.utc) if qr.enabled_at else None,
                    "notes": qr.notes,
                    "remarks": remarks_by_qr.get(qr.id, []),
                }
                for qr in active_qrs
            ], int(total or 0)

    @staticmethod
    async def release_session(qr_id: str, released_by: UUID) -> int:
        """Archive remarks to produced_items, delete remarks, and set QR to inactive.

        Returns the number of remarks archived.
        Raises ValueError if the QR is not active or has no remarks.
        """
        logger.info(f"[RELEASE] Starting release_session for qr_id={qr_id}, released_by={released_by}")
        async with db_manager.session_factory() as db:
            # 1. Fetch the QR tag with row-level lock to prevent concurrent releases
            qr_result = await db.execute(select(QRCode).where(QRCode.id == qr_id).with_for_update())
            qr_code = qr_result.scalar_one_or_none()
            if qr_code is None:
                logger.error(f"[RELEASE] QR Code not found: id={qr_id}")
                raise ValueError("QR Code not found.")
            logger.info(f"[RELEASE] QR found: id={qr_code.id}, status={qr_code.status}")
            if str(qr_code.status) != "active":
                logger.warning(f"[RELEASE] QR is not active (status={qr_code.status}), aborting")
                raise ValueError("QR tag is not active — nothing to release.")

            # 2. Fetch all remarks for this QR
            remarks = (
                await db.scalars(
                    select(Remarks)
                    .where(Remarks.qr_id == qr_id)
                    .order_by(Remarks.created_at.asc())
                )
            ).all()
            logger.info(f"[RELEASE] Found {len(remarks)} remarks for qr_id={qr_id}")

            if not remarks:
                logger.error(f"[RELEASE] No remarks to archive for qr_id={qr_id}")
                raise ValueError("No remarks found for this QR session — nothing to archive.")

            # 3. Resolve department names for all remarks
            dept_ids = list({r.department_id for r in remarks if r.department_id})
            dept_name_map: dict = {}
            if dept_ids:
                dept_rows = await db.execute(
                    select(Department.id, Department.name).where(Department.id.in_(dept_ids))
                )
                dept_name_map = {row.id: row.name for row in dept_rows.all()}

            # 4. Copy each remark into produced_items
            for i, remark in enumerate(remarks):
                dept_name = dept_name_map.get(remark.department_id, "Unknown")
                logger.debug(f"[RELEASE] Archiving remark {i+1}/{len(remarks)}: id={remark.id}, item_id={remark.item_id}, dept={dept_name}")
                produced_item = ProducedItems(
                    qr_id=qr_id,
                    item_id=remark.item_id,
                    department_name=dept_name,
                    field_1=remark.field_1,
                    field_2=remark.field_2,
                    field_3=remark.field_3,
                    field_4=remark.field_4,
                    field_5=remark.field_5,
                    issue_remarks=remark.issue_remarks,
                    created_by=remark.remark_by,
                    updated_by=remark.remark_updated,
                    remark_by=remark.remark_by,
                    remark_updated=remark.remark_updated,
                    created_at=remark.created_at,
                )
                db.add(produced_item)

            # 4. Delete all remarks for this QR
            await db.execute(delete(Remarks).where(Remarks.qr_id == qr_id))
            logger.info(f"[RELEASE] Deleted remarks from remarks table for qr_id={qr_id}")

            # 5. Reset QR tag to inactive
            qr_code.status = "inactive"
            qr_code.disabled_by = released_by
            qr_code.disabled_at = datetime.utcnow()
            qr_code.enabled_by = None
            qr_code.enabled_at = None
            qr_code.notes = None

            await db.commit()
            logger.info(f"[RELEASE] SUCCESS: Archived {len(remarks)} items to produced_items for qr_id={qr_id}")
            return len(remarks)
