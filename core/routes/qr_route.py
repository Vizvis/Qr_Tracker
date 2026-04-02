"""QR Code API routes."""
from fastapi import APIRouter, status, Depends, Query
from core.services.qr_service import QRService
from models.api_models.qr_models import (
    QRCodeCreateRequest,
    QRCodeStatusUpdate,
    QRCodeToggleRequest,
    QRCodeResponse,
    QRSessionFinalizeResponse,
    QRCodeListResponse,
)
from uuid import UUID
from auth.dependencies import require_admin, require_supervisor
from core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

qr_router = APIRouter(prefix="/api/qr", tags=["QR Codes"])


@qr_router.post("", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_qr(
    payload: QRCodeCreateRequest,
    current_user_id: UUID = Depends(require_admin)
):
    """Create QR code endpoint (Admin only)."""
    qr_code = await QRService.create_qr(payload, current_user_id=current_user_id)
    return qr_code


@qr_router.get("", response_model=QRCodeListResponse)
async def get_all_qrs(
    current_user_id: UUID = Depends(require_supervisor),
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
):
    """Get all QR codes (Supervisor+)."""
    _ = current_user_id
    return await QRService.get_all_qrs_paginated(page, page_size)


@qr_router.get("/{id}", response_model=QRCodeResponse)
async def get_qr_by_id(
    id: str,
    current_user_id: UUID = Depends(require_supervisor)
):
    """Get specific QR code by ID (Supervisor+)."""
    return await QRService.get_qr_by_id(id)


@qr_router.patch("/{id}/enable", response_model=QRCodeResponse)
async def enable_qr(
    id: str,
    payload: QRCodeStatusUpdate,
    current_user_id: UUID = Depends(require_supervisor)
):
    """Set QR Code status to active (Supervisor+)."""
    return await QRService.update_qr_status(id, "active", payload, current_user_id=current_user_id)


@qr_router.patch("/{id}/disable", response_model=QRCodeResponse)
async def disable_qr(
    id: str,
    payload: QRCodeStatusUpdate,
    current_user_id: UUID = Depends(require_supervisor)
):
    """Set QR Code status to inactive (Supervisor+)."""
    return await QRService.update_qr_status(id, "inactive", payload, current_user_id=current_user_id)


@qr_router.post("/enable", response_model=QRCodeResponse)
async def enable_qr_by_input(
    payload: QRCodeToggleRequest,
    current_user_id: UUID = Depends(require_supervisor),
):
    """Enable QR code from user_id and qr_code_id payload (Supervisor+)."""
    return await QRService.enable_qr_from_input(payload, current_user_id=current_user_id)


@qr_router.post("/disable", response_model=QRCodeResponse)
async def disable_qr_by_input(
    payload: QRCodeToggleRequest,
    current_user_id: UUID = Depends(require_supervisor),
):
    """Disable QR code from user_id and qr_code_id payload (Supervisor+)."""
    return await QRService.disable_qr_from_input(payload, current_user_id=current_user_id)


@qr_router.post("/{id}/finish-session", response_model=QRSessionFinalizeResponse)
async def finish_session(
    id: str,
    current_user_id: UUID = Depends(require_supervisor),
):
    """Move current QR remarks to produced_items and clear remarks for that QR."""
    moved_count = await QRService.finish_session(id)
    return QRSessionFinalizeResponse(
        qr_id=id,
        moved_count=moved_count,
        message="Session finalized successfully.",
    )