"""Produced items service layer for query workflows."""
from core.pagination import build_pagination, normalize_page_size
from db_handler.produced_items_db_handler import ProducedItemsDBHandler
from models.db_models.produced_items import ProducedItems


class ProducedItemsService:
    """Business logic for produced items endpoints."""

    @staticmethod
    async def get_by_qr_id(qr_id: str) -> list[ProducedItems]:
        return await ProducedItemsDBHandler.get_by_qr_id(qr_id)

    @staticmethod
    async def get_by_qr_id_paginated(qr_id: str, page: int, page_size: int) -> dict:
        normalized_page_size = normalize_page_size(page_size)
        items, total = await ProducedItemsDBHandler.get_by_qr_id_paginated(qr_id, page, normalized_page_size)
        return {
            "items": ProducedItemsService._group_by_item_id(items),
            **build_pagination(page, normalized_page_size, total),
        }

    @staticmethod
    async def get_by_item_id(item_id: str) -> list[ProducedItems]:
        return await ProducedItemsDBHandler.get_by_item_id(item_id)

    @staticmethod
    async def get_by_item_id_paginated(item_id: str, page: int, page_size: int) -> dict:
        normalized_page_size = normalize_page_size(page_size)
        items, total = await ProducedItemsDBHandler.get_by_item_id_paginated(item_id, page, normalized_page_size)
        return {
            "items": ProducedItemsService._group_by_item_id(items),
            **build_pagination(page, normalized_page_size, total),
        }

    @staticmethod
    def _group_by_item_id(items: list[ProducedItems]) -> dict[str, list[dict]]:
        grouped: dict[str, list[dict]] = {}
        for item in items:
            key = item.item_id
            grouped.setdefault(key, []).append(
                {
                    "produced_id": str(item.produced_id),
                    "qr_id": item.qr_id,
                    "item_id": item.item_id,
                    "department_id": str(item.department_id),
                    "general_remarks": item.general_remarks,
                    "issue_remarks": item.issue_remarks,
                    "created_by": str(item.created_by) if item.created_by else None,
                    "updated_by": str(item.updated_by) if item.updated_by else None,
                    "remark_by": str(item.remark_by) if item.remark_by else None,
                    "remark_updated": str(item.remark_updated) if item.remark_updated else None,
                    "created_at": item.created_at,
                }
            )
        return grouped
