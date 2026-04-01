"""Session API routes for remarks timeline and final-state retrieval."""
from typing import Annotated
from fastapi import APIRouter, Depends, status
from auth.cookie_auth import require_valid_auth_cookie
from core.services.session_service import SessionService
from models.api_models.session_models import (
    SessionRemarkCreateRequest,
    SessionRemarkResponse,
)


session_router = APIRouter(prefix="/api/session", tags=["Session"])


@session_router.get("/active-qrs", response_model=dict)
async def get_active_qrs_with_remarks(
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Return all active QRs with their current session remarks."""
    return await SessionService.get_active_qrs_with_remarks()


@session_router.post("/{qr_id}/remarks", response_model=SessionRemarkResponse, status_code=status.HTTP_201_CREATED)
async def create_remark(
    qr_id: str,
    payload: SessionRemarkCreateRequest,
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Create a department remark for an active QR session."""
    return await SessionService.create_remark(qr_id, payload)


@session_router.get("/{qr_id}")
async def get_session(
    qr_id: str,
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Return all remarks for a qr_id in ascending created_at order."""
    return await SessionService.get_session(qr_id)


@session_router.get("/{qr_id}/previous-state")
async def get_previous_state(
    qr_id: str,
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Return only the latest (final) remark row for a qr_id."""
    return await SessionService.get_previous_state(qr_id)
