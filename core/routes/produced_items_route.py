"""Produced items API routes for querying by qr_id and item_id."""
from uuid import UUID
from fastapi import APIRouter, Depends
from auth.dependencies import require_supervisor
from core.services.produced_items_service import ProducedItemsService
from models.api_models.produced_items_models import ProducedItemResponse


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
                created_at=item.created_at,
            )
        )

    return grouped


@produced_items_router.get("/qr/{qr_id}", response_model=dict[str, list[ProducedItemResponse]])
async def get_produced_items_by_qr_id(
    qr_id: str,
    current_user_id: UUID = Depends(require_supervisor),
):
    """View produced items for a qr_id."""
    _ = current_user_id
    items = await ProducedItemsService.get_by_qr_id(qr_id)
    return _group_by_item_id(items)


@produced_items_router.get("/item/{item_id}", response_model=dict[str, list[ProducedItemResponse]])
async def get_produced_items_by_item_id(
    item_id: str,
    current_user_id: UUID = Depends(require_supervisor),
):
    """View produced items for an item_id."""
    _ = current_user_id
    items = await ProducedItemsService.get_by_item_id(item_id)
    return _group_by_item_id(items)
