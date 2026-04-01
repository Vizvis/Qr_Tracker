"""Produced items service layer for query workflows."""
from db_handler.produced_items_db_handler import ProducedItemsDBHandler
from models.db_models.produced_items import ProducedItems


class ProducedItemsService:
    """Business logic for produced items endpoints."""

    @staticmethod
    async def get_by_qr_id(qr_id: str) -> list[ProducedItems]:
        return await ProducedItemsDBHandler.get_by_qr_id(qr_id)

    @staticmethod
    async def get_by_item_id(item_id: str) -> list[ProducedItems]:
        return await ProducedItemsDBHandler.get_by_item_id(item_id)
