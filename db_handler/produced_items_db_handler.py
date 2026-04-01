"""Database access layer for produced items queries."""
from sqlalchemy import select
from db_handler.database import db_manager
from models.db_models.produced_items import ProducedItems


class ProducedItemsDBHandler:
    """Handles produced items read operations."""

    @staticmethod
    async def get_by_qr_id(qr_id: str) -> list[ProducedItems]:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(ProducedItems)
                .where(ProducedItems.qr_id == qr_id)
                .order_by(ProducedItems.created_at.asc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_item_id(item_id: str) -> list[ProducedItems]:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(ProducedItems)
                .where(ProducedItems.item_id == item_id)
                .order_by(ProducedItems.created_at.asc())
            )
            return list(result.scalars().all())
