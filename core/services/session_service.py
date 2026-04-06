"""Session service layer for remarks history endpoints."""
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from datetime import timezone

from core.pagination import build_pagination, normalize_page_size
from db_handler.department_db_handler import DepartmentDBHandler
from db_handler.qr_db_handler import QRDBHandler
from db_handler.session_db_handler import SessionDBHandler
from models.api_models.session_models import SessionRemarkCreateRequest, SessionRemarkUpdateRequest
from models.api_models.remarks_models import RemarkCreateRequest, RemarkUpdateRequest
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
            "custom_data": remark.custom_data if remark.custom_data is not None else {},
            "remarks_history": remark.remarks_history if remark.remarks_history is not None else [],
            "remark_by": str(remark.remark_by) if getattr(remark, "remark_by", None) is not None else None,
            "remark_updated": str(remark.remark_updated) if getattr(remark, "remark_updated", None) is not None else None,
            "created_at": remark.created_at.replace(tzinfo=timezone.utc) if remark.created_at is not None else None,
            "updated_at": remark.updated_at.replace(tzinfo=timezone.utc) if getattr(remark, 'updated_at', None) is not None else None,
        }

    @staticmethod
    async def create_remark(current_user_id: UUID, payload: RemarkCreateRequest) -> dict:
        qr_code = await QRDBHandler.get_by_id(payload.qr_id)
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

        existing_item_id = await SessionDBHandler.get_existing_item_id_for_qr(payload.qr_id)
        if existing_item_id is not None and existing_item_id != payload.item_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Item different different from previous department remark",
            )

        if await SessionDBHandler.has_department_update(payload.qr_id, payload.department_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Remark by this dept alr provided",
            )

        if await SessionDBHandler.has_item_department_update(payload.qr_id, payload.item_id, payload.department_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate update: item_id + department_id already exists for this active QR session.",
            )

        try:
            remark, department_name = await SessionDBHandler.create_remark(
                qr_id=payload.qr_id,
                item_id=payload.item_id,
                department_id=payload.department_id,
                general_remarks=payload.general_remarks,
                issue_remarks=payload.issue_remarks,
                custom_data=payload.custom_data,
                current_user_id=current_user_id,
            )
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate remark entry for the same QR, item, and department.",
            ) from exc
        return SessionService._remark_to_dict(remark, department_name)

    @staticmethod
    async def create_session_remark(qr_id: str, current_user_id: UUID, payload: SessionRemarkCreateRequest) -> dict:
        return await SessionService.create_remark(
            current_user_id=current_user_id,
            payload=RemarkCreateRequest(
                qr_id=qr_id,
                item_id=payload.item_id,
                department_id=payload.department_id,
                general_remarks=payload.general_remarks,
                issue_remarks=payload.issue_remarks,
                custom_data=payload.custom_data,
            ),
        )

    @staticmethod
    async def update_session_remark(
        qr_id: str, remark_id: UUID, current_user_id: UUID, payload: SessionRemarkUpdateRequest
    ) -> dict:
        """Update a remark via the session endpoint (PUT /session/{qr_id}/remarks/{remark_id})."""
        remark = await SessionDBHandler.get_by_id(remark_id)
        if remark is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Remark not found.",
            )

        # Ensure the remark actually belongs to this qr_id
        if str(remark.qr_id) != qr_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Remark not found for this QR session.",
            )

        update_data = {
            "general_remarks": payload.general_remarks,
            "issue_remarks": payload.issue_remarks,
        }

        try:
            updated_row, department_name = await SessionDBHandler.update_remark(
                remark_id=remark_id,
                update_data=update_data,
                current_user_id=current_user_id,
            )
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate remark entry for the same QR, item, and department.",
            ) from exc
        if updated_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Remark not found.",
            )

        return SessionService._remark_to_dict(updated_row, department_name)

    @staticmethod
    async def update_remark(remark_id: UUID, current_user_id: UUID, payload: RemarkUpdateRequest) -> dict:
        remark = await SessionDBHandler.get_by_id(remark_id)
        if remark is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Remark not found.",
            )

        update_data = {}
        set_fields = payload.model_fields_set

        if "item_id" in set_fields:
            update_data["item_id"] = payload.item_id

        if "department_id" in set_fields:
            if payload.department_id is not None:
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
            update_data["department_id"] = payload.department_id

        if "general_remarks" in set_fields:
            update_data["general_remarks"] = payload.general_remarks

        if "issue_remarks" in set_fields:
            update_data["issue_remarks"] = payload.issue_remarks

        if "custom_data" in set_fields:
            update_data["custom_data"] = payload.custom_data

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes submitted.",
            )

        if payload.department_id is not None and payload.department_id != remark.department_id:
            if await SessionDBHandler.has_department_update(str(remark.qr_id), payload.department_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Duplicate update: this department has already updated this active QR session.",
                )

        try:
            updated_row, department_name = await SessionDBHandler.update_remark(
                remark_id=remark_id,
                update_data=update_data,
                current_user_id=current_user_id,
            )
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate remark entry for the same QR, item, and department.",
            ) from exc
        if updated_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Remark not found.",
            )

        return SessionService._remark_to_dict(updated_row, department_name)

    @staticmethod
    async def release_session(qr_id: str, current_user_id: UUID) -> dict:
        """Release a QR session: archive remarks, clear data, set QR inactive."""
        qr_code = await QRDBHandler.get_by_id(qr_id)
        if qr_code is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code not found.",
            )

        if str(qr_code.status) != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QR tag is not active — nothing to release.",
            )

        try:
            archived_count = await SessionDBHandler.release_session(qr_id, released_by=current_user_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        return {
            "qr_id": qr_id,
            "archived_count": archived_count,
            "message": "Tag released and production data archived.",
        }

    @staticmethod
    async def get_session(qr_id: str) -> dict:
        # Check if the QR exists and is active
        qr_code = await QRDBHandler.get_by_id(qr_id)
        if qr_code is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code not found.",
            )

        # Inactive QR → no active session to show
        if str(qr_code.status) != "active":
            return {"qr_id": qr_id, "remarks": []}

        remarks = await SessionDBHandler.list_remarks_by_qr_id(qr_id)
        return {
            "qr_id": qr_id,
            "remarks": [
                SessionService._remark_to_dict(remark, department_name)
                for remark, department_name in remarks
            ],
        }

    @staticmethod
    async def get_remarks(page: int, page_size: int) -> dict:
        normalized_page_size = normalize_page_size(page_size)
        rows, total = await SessionDBHandler.list_all_remarks(page, normalized_page_size)
        return {
            "items": [SessionService._remark_to_dict(remark, department_name) for remark, department_name in rows],
            **build_pagination(page, normalized_page_size, total),
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
    async def get_active_qrs_with_remarks(page: int, page_size: int) -> dict:
        normalized_page_size = normalize_page_size(page_size)
        active_qrs, total = await SessionDBHandler.list_active_qr_remarks(page, normalized_page_size)
        return {
            "items": active_qrs,
            **build_pagination(page, normalized_page_size, total),
            "count": len(active_qrs),
            "active_qrs": active_qrs,
        }
