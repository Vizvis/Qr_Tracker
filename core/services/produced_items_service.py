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
                    "department_name": item.department_name,
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

    @staticmethod
    async def search_production_history(
        search: str | None, start_date: str | None, end_date: str | None, page: int, page_size: int
    ) -> dict:
        normalized_page_size = normalize_page_size(page_size)
        rows, total = await ProducedItemsDBHandler.search_production_history(
            search, start_date, end_date, page, normalized_page_size
        )

        # Re-use your python grouping logic, then map to Frontend shape
        grouped = ProducedItemsService._group_by_item_id(rows)
        
        items = []
        for item_id, remarks_data in grouped.items():
            qr_id = remarks_data[0]["qr_id"] if remarks_data else ""
            
            # Use max and min dates from remarks
            created_at = min(r["created_at"] for r in remarks_data) if remarks_data else None
            released_at = max(r["created_at"] for r in remarks_data) if remarks_data else None
            
            issues_count = sum(1 for r in remarks_data if r.get("issue_remarks"))
            
            items.append({
                "id": item_id,
                "qr_id": qr_id,
                "batch_number": None,
                "product_name": None,
                "remarks_data": remarks_data,
                "activated_by": None,
                "activated_at": None,
                "released_by": None,
                "released_at": released_at,
                "total_departments": len(remarks_data),
                "departments_with_issues": issues_count,
                "created_at": created_at
            })

        # Calculate pages
        pages = (total + normalized_page_size - 1) // normalized_page_size if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": normalized_page_size,
            "pages": pages
        }
