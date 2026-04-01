"""Session service layer for remarks history endpoints."""
from fastapi import HTTPException, status

from db_handler.department_db_handler import DepartmentDBHandler
from db_handler.qr_db_handler import QRDBHandler
from db_handler.session_db_handler import SessionDBHandler
from models.api_models.session_models import SessionRemarkCreateRequest
from models.db_models.enums import DepartmentStatus
from models.db_models.remarks import Remarks


class SessionService:
    """Business logic for session endpoints."""

    @staticmethod
    def _remark_to_dict(remark: Remarks, department_name: str | None) -> dict:
        return {
            "id": str(remark.id),
            "qr_id": str(remark.qr_id) if remark.qr_id is not None else None,
            "item_id": remark.item_id,
            "department_id": str(remark.department_id) if remark.department_id is not None else None,
            "department": department_name,
            "general_remarks": remark.general_remarks,
            "issue_remarks": remark.issue_remarks,
            "created_at": remark.created_at.isoformat() if remark.created_at is not None else None,
        }

    @staticmethod
    async def create_remark(qr_id: str, payload: SessionRemarkCreateRequest) -> dict:
        qr_code = await QRDBHandler.get_by_id(qr_id)
        if qr_code is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code not found.",
            )

        if str(qr_code.status) != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Remarks can be added only when QR is active.",
            )

        department = await DepartmentDBHandler.get_by_id(payload.department_id)
        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        department_status = getattr(department.status, "value", str(department.status)).lower()
        if department_status != DepartmentStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department is inactive.",
            )

        if await SessionDBHandler.has_department_update(qr_id, payload.department_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate update: this department has already updated this active QR session.",
            )

        if await SessionDBHandler.has_item_department_update(qr_id, payload.item_id, payload.department_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate update: item_id + department_id already exists for this active QR session.",
            )

        remark, department_name = await SessionDBHandler.create_remark(
            qr_id=qr_id,
            item_id=payload.item_id,
            department_id=payload.department_id,
            general_remarks=payload.general_remarks,
            issue_remarks=payload.issue_remarks,
        )
        return SessionService._remark_to_dict(remark, department_name)

    @staticmethod
    async def get_session(qr_id: str) -> dict:
        remarks = await SessionDBHandler.list_remarks_by_qr_id(qr_id)
        return {
            "qr_id": qr_id,
            "remarks": [
                SessionService._remark_to_dict(remark, department_name)
                for remark, department_name in remarks
            ],
        }

    @staticmethod
    async def get_previous_state(qr_id: str) -> dict:
        latest_remark = await SessionDBHandler.get_latest_remark_by_qr_id(qr_id)
        return {
            "qr_id": qr_id,
            "final_state": (
                SessionService._remark_to_dict(latest_remark[0], latest_remark[1])
                if latest_remark
                else None
            ),
        }

    @staticmethod
    async def get_active_qrs_with_remarks() -> dict:
        active_qrs = await SessionDBHandler.list_active_qr_remarks()
        return {
            "count": len(active_qrs),
            "active_qrs": active_qrs,
        }
