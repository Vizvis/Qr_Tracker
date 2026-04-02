"""QR Code service layer for business logic workflows."""
from fastapi import HTTPException, status
from db_handler.qr_db_handler import QRDBHandler
from models.db_models.qr_code import QRCode
from models.api_models.qr_models import QRCodeCreateRequest, QRCodeStatusUpdate, QRTagStatusUpdate
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
            status="inactive",
            registered_by=current_user_id,
            notes=payload.notes,
        )
        return await QRDBHandler.create(new_qr)

    @staticmethod
    async def get_all_qrs() -> list[QRCode]:
        return await QRDBHandler.get_all()

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
    async def update_qr_status(qr_id: str, new_status: str, payload: QRCodeStatusUpdate | QRTagStatusUpdate, current_user_id: UUID) -> QRCode:
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
    async def delete_qr(qr_id: str) -> None:
        deleted = await QRDBHandler.delete_qr(qr_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag ID not found",
            )