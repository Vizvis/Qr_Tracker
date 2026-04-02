"""Remark CRUD API routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from auth.cookie_auth import require_valid_auth_cookie
from core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from core.services.session_service import SessionService
from models.api_models.remarks_models import RemarkCreateRequest, RemarkListResponse, RemarkResponse, RemarkUpdateRequest


remarks_router = APIRouter(prefix="/api/remarks", tags=["Remarks"])


@remarks_router.get("", response_model=RemarkListResponse)
async def get_remarks(
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
):
    """Get all remarks with pagination."""
    return await SessionService.get_remarks(page=page, page_size=page_size)


@remarks_router.post("", response_model=RemarkResponse, status_code=status.HTTP_201_CREATED)
async def create_remark(
    payload: RemarkCreateRequest,
    current_user: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Create remark endpoint."""
    current_user_id = UUID(current_user["user_id"])
    return await SessionService.create_remark(current_user_id=current_user_id, payload=payload)


@remarks_router.patch("/{remark_id}", response_model=RemarkResponse)
async def update_remark(
    remark_id: Annotated[UUID, Path(..., description="Remark ID")],
    payload: RemarkUpdateRequest,
    current_user: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Update a remark row."""
    current_user_id = UUID(current_user["user_id"])
    return await SessionService.update_remark(remark_id=remark_id, current_user_id=current_user_id, payload=payload)