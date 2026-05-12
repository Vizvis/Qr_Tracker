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

# Field names for iteration
FIELD_NAMES = [f"field_{i}" for i in range(1, 6)]


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
            "field_1": remark.field_1 if remark.field_1 is not None else 0,
            "field_2": remark.field_2 if remark.field_2 is not None else 0,
            "field_3": remark.field_3 if remark.field_3 is not None else 0,
            "field_4": remark.field_4 if remark.field_4 is not None else 0,
            "field_5": remark.field_5 if remark.field_5 is not None else 0,
            "issue_remarks": remark.issue_remarks,
            "custom_data": remark.custom_data if remark.custom_data is not None else {},
            "remarks_history": remark.remarks_history if remark.remarks_history is not None else [],
            "scanned_by": str(remark.scanned_by) if getattr(remark, "scanned_by", None) is not None else None,
            "last_edited_by": str(remark.last_edited_by) if getattr(remark, "last_edited_by", None) is not None else None,
            "created_at": remark.created_at.replace(tzinfo=timezone.utc) if remark.created_at is not None else None,
            "updated_at": remark.updated_at.replace(tzinfo=timezone.utc) if getattr(remark, 'updated_at', None) is not None else None,
        }



    @staticmethod
    async def _validate_vertical_cascade(qr_id: str, item_id: str, department_id: UUID, field_values: dict):
        """Validate across-department cascade: each field <= last non-zero value in any previous department."""
        prev_remarks = await SessionDBHandler.get_all_previous_department_remarks(qr_id, item_id, department_id)
        if not prev_remarks:
            return  # First department, no constraint

        for i in range(1, 6):
            field_name = f"field_{i}"
            current_val = field_values.get(field_name)
            if current_val is None or current_val == 0:
                continue
            # Walk backwards through previous remarks to find last non-zero value
            prev_val = None
            for remark in prev_remarks:
                val = getattr(remark, field_name, None)
                if val is not None and val > 0:
                    prev_val = val
                    break
            if prev_val is not None and current_val > prev_val:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field {i} value ({current_val}) exceeds previous department's value ({prev_val}).",
                )

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

        if await SessionDBHandler.has_department_update(payload.qr_id, payload.department_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate update: this department has already updated this active QR session.",
            )

        if await SessionDBHandler.has_item_department_update(payload.qr_id, payload.item_id, payload.department_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate update: item_id + department_id already exists for this active QR session.",
            )

        if await SessionDBHandler.is_item_id_used_by_other_qr(payload.item_id, payload.qr_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item ID {payload.item_id} is already in use (either currently active on another QR or already archived/completed).",
            )

        # Build field values dict for validation
        field_values = {
            f"field_{i}": getattr(payload, f"field_{i}") for i in range(1, 6)
        }

        # Vertical cascade validation (same field across departments)
        await SessionService._validate_vertical_cascade(
            payload.qr_id, payload.item_id, payload.department_id, field_values
        )

        try:
            remark, department_name = await SessionDBHandler.create_remark(
                qr_id=payload.qr_id,
                item_id=payload.item_id,
                department_id=payload.department_id,
                field_1=payload.field_1,
                field_2=payload.field_2,
                field_3=payload.field_3,
                field_4=payload.field_4,
                field_5=payload.field_5,
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
                field_1=payload.field_1,
                field_2=payload.field_2,
                field_3=payload.field_3,
                field_4=payload.field_4,
                field_5=payload.field_5,
                issue_remarks=payload.issue_remarks,
                custom_data=payload.custom_data,
            ),
        )

    @staticmethod
    async def update_session_remark(
        qr_id: str, remark_id: UUID, current_user_id: UUID, payload: SessionRemarkUpdateRequest,
        user_role: str = "operator"
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

        # Edit-lock: operators cannot edit once the next department has scanned
        if user_role != "admin":
            is_locked = await SessionDBHandler.has_subsequent_department_remark(
                qr_id, remark.item_id, remark.department_id
            )
            if is_locked:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Editing locked: a subsequent department has already logged data for this item.",
                )

        update_data = {}
        for i in range(1, 6):
            field_name = f"field_{i}"
            val = getattr(payload, field_name, None)
            if val is not None:
                update_data[field_name] = val
        update_data["issue_remarks"] = payload.issue_remarks

        # Merge existing values with updates for cascade validation
        field_values = {}
        for i in range(1, 6):
            field_name = f"field_{i}"
            field_values[field_name] = update_data.get(field_name, getattr(remark, field_name, 0))

        # Vertical cascade validation (same field across departments)
        await SessionService._validate_vertical_cascade(
            qr_id, remark.item_id, remark.department_id, field_values
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

        for i in range(1, 6):
            field_name = f"field_{i}"
            if field_name in set_fields:
                update_data[field_name] = getattr(payload, field_name)

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
    async def release_session(qr_id: str, current_user_id: UUID, force: bool = False) -> dict:
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
            archived_count = await SessionDBHandler.release_session(qr_id, released_by=current_user_id, force=force)
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
