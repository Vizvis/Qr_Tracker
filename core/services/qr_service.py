"""QR Code service layer for business logic workflows."""
from fastapi import HTTPException, status
from core.pagination import build_pagination, normalize_page_size
from db_handler.qr_db_handler import QRDBHandler
from models.db_models.qr_code import QRCode
from models.api_models.qr_models import QRCodeCreateRequest, QRCodeStatusUpdate, QRCodeToggleRequest
from uuid import UUID


class QRService:
    """Business logic for QR Code endpoints."""

    @staticmethod
    async def create_qr(payload: QRCodeCreateRequest, current_user_id: UUID) -> QRCode:
        existing_qr = await QRDBHandler.get_by_id(payload.id)
        if existing_qr is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A QR code with this ID already exists.",
            )

        new_qr = QRCode(
            id=payload.id,
            status="pending",
            registered_by=current_user_id,
            notes=payload.notes,
        )
        return await QRDBHandler.create(new_qr)

    @staticmethod
    async def get_all_qrs() -> list[QRCode]:
        return await QRDBHandler.get_all()

    @staticmethod
    async def get_all_qrs_paginated(page: int, page_size: int) -> dict:
        normalized_page_size = normalize_page_size(page_size)
        qrs, total = await QRDBHandler.list_paginated(page, normalized_page_size)
        return {
            "items": [
                {
                    "id": qr.id,
                    "status": qr.status,
                    "registered_by": qr.registered_by,
                    "enabled_by": qr.enabled_by,
                    "enabled_at": qr.enabled_at,
                    "disabled_by": qr.disabled_by,
                    "disabled_at": qr.disabled_at,
                    "created_at": qr.created_at,
                    "notes": qr.notes,
                }
                for qr in qrs
            ],
            **build_pagination(page, normalized_page_size, total),
        }

    @staticmethod
    async def get_qr_by_id(qr_id: str) -> QRCode:
        qr_code = await QRDBHandler.get_by_id(qr_id)
        if qr_code is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code not found.",
            )
        return qr_code

    @staticmethod
    async def update_qr_status(qr_id: str, new_status: str, payload: QRCodeStatusUpdate, current_user_id: UUID) -> QRCode:
        if new_status not in ["active", "inactive"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'active' or 'inactive'.",
            )
            
        qr_code = await QRDBHandler.get_by_id(qr_id)
        if qr_code is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code not found.",
            )

        updated_qr = await QRDBHandler.update_status(
            qr_id=qr_id,
            new_status=new_status,
            action_by=current_user_id,
            notes=payload.notes,
        )
        
        if updated_qr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code not found.",
            )
        return updated_qr

    @staticmethod
    async def finish_session(qr_id: str) -> int:
        qr_code = await QRDBHandler.get_by_id(qr_id)
        if qr_code is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code not found.",
            )

        try:
            return await QRDBHandler.finish_session(qr_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    @staticmethod
    async def enable_qr_from_input(payload: QRCodeToggleRequest, current_user_id: UUID) -> QRCode:
        if payload.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="user_id must match the authenticated user.",
            )

        return await QRService.update_qr_status(
            qr_id=payload.qr_code_id,
            new_status="active",
            payload=QRCodeStatusUpdate(notes=payload.notes),
            current_user_id=current_user_id,
        )

    @staticmethod
    async def disable_qr_from_input(payload: QRCodeToggleRequest, current_user_id: UUID) -> QRCode:
        if payload.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="user_id must match the authenticated user.",
            )

        return await QRService.update_qr_status(
            qr_id=payload.qr_code_id,
            new_status="inactive",
            payload=QRCodeStatusUpdate(notes=payload.notes),
            current_user_id=current_user_id,
        )