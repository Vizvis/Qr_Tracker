"""Produced items API routes for querying by qr_id and item_id."""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from auth.dependencies import require_supervisor, require_admin
from core.services.produced_items_service import ProducedItemsService
from models.api_models.produced_items_models import (
    ProducedItemResponse, 
    ProducedItemsGroupedResponse,
    ProducedItemsPaginatedResponse, 
    ProductionHistoryPaginatedResponse
)

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
                department_name=item.department_name,
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


@produced_items_router.get("/item/{item_id}", response_model=ProducedItemsGroupedResponse)
async def get_produced_items_by_item_id(
    item_id: str,
    current_user_id: UUID = Depends(require_supervisor),
):
    """View produced items for an item_id."""
    _ = current_user_id
    return await ProducedItemsService.get_by_item_id_grouped(item_id)


@produced_items_router.get("", response_model=ProductionHistoryPaginatedResponse)
async def get_production_history(
    current_user_id: UUID = Depends(require_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    search: str | None = Query(None, description="Search term for qr_id, item_id or remarks"),
    start_date: str | None = Query(None, description="Filter by start date (ISO formatted string)"),
    end_date: str | None = Query(None, description="Filter by end date (ISO formatted string)"),
):
    """View and search paginated production history (Admin only)."""
    _ = current_user_id
    return await ProducedItemsService.search_production_history(
        search=search,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=limit,
    )
