"""Session API routes for remarks timeline and final-state retrieval."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from auth.cookie_auth import require_valid_auth_cookie
from core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from core.services.session_service import SessionService
from models.api_models.session_models import (
    SessionRemarkCreateRequest,
    SessionRemarkResponse,
    ActiveQRRemarksListResponse,
)


session_router = APIRouter(prefix="/api/session", tags=["Session"])


@session_router.get("/active-qrs", response_model=ActiveQRRemarksListResponse)
async def get_active_qrs_with_remarks(
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
):
    """Return all active QRs with their current session remarks."""
    return await SessionService.get_active_qrs_with_remarks(page=page, page_size=page_size)


@session_router.post("/{qr_id}/remarks", response_model=SessionRemarkResponse, status_code=status.HTTP_201_CREATED)
async def create_remark(
    qr_id: str,
    payload: SessionRemarkCreateRequest,
    current_user: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Create a department remark for an active QR session."""
    current_user_id = UUID(current_user["user_id"])
    return await SessionService.create_session_remark(qr_id, current_user_id, payload)


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
