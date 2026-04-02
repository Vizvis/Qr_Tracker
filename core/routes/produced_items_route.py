"""Produced items API routes for querying by qr_id and item_id."""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from auth.dependencies import require_supervisor
from core.services.produced_items_service import ProducedItemsService
from models.api_models.produced_items_models import ProducedItemResponse, ProducedItemsPaginatedResponse


produced_items_router = APIRouter(prefix="/api/produced-items", tags=["Produced Items"])


def _group_by_item_id(items) -> dict[str, list[ProducedItemResponse]]:
    grouped: dict[str, list[ProducedItemResponse]] = {}
    for item in items:
        key = item.item_id
        if key not in grouped:
            grouped[key] = []

        grouped[key].append(
            ProducedItemResponse(
                produced_id=str(item.produced_id),
                qr_id=item.qr_id,
                item_id=item.item_id,
                department_id=str(item.department_id),
                general_remarks=item.general_remarks,
                issue_remarks=item.issue_remarks,
                created_by=str(item.created_by) if item.created_by else None,
                updated_by=str(item.updated_by) if item.updated_by else None,
                remark_by=str(item.remark_by) if item.remark_by else None,
                remark_updated=str(item.remark_updated) if item.remark_updated else None,
                created_at=item.created_at,
            )
        )

    return grouped


@produced_items_router.get("/qr/{qr_id}", response_model=ProducedItemsPaginatedResponse)
async def get_produced_items_by_qr_id(
    qr_id: str,
    current_user_id: UUID = Depends(require_supervisor),
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
):
    """View produced items for a qr_id."""
    _ = current_user_id
    return await ProducedItemsService.get_by_qr_id_paginated(qr_id, page, page_size)


@produced_items_router.get("/item/{item_id}", response_model=ProducedItemsPaginatedResponse)
async def get_produced_items_by_item_id(
    item_id: str,
    current_user_id: UUID = Depends(require_supervisor),
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
):
    """View produced items for an item_id."""
    _ = current_user_id
    return await ProducedItemsService.get_by_item_id_paginated(item_id, page, page_size)
