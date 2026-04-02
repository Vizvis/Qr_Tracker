"""Database access layer for produced items queries."""
from sqlalchemy import func, select
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
    async def get_by_qr_id_paginated(qr_id: str, page: int, page_size: int) -> tuple[list[ProducedItems], int]:
        offset = (page - 1) * page_size
        async with db_manager.session_factory() as db:
            total = int(
                await db.scalar(
                    select(func.count()).select_from(ProducedItems).where(ProducedItems.qr_id == qr_id)
                )
                or 0
            )
            result = await db.execute(
                select(ProducedItems)
                .where(ProducedItems.qr_id == qr_id)
                .order_by(ProducedItems.created_at.asc())
                .offset(offset)
                .limit(page_size)
            )
            return list(result.scalars().all()), total

    @staticmethod
    async def get_by_item_id(item_id: str) -> list[ProducedItems]:
        async with db_manager.session_factory() as db:
            result = await db.execute(
                select(ProducedItems)
                .where(ProducedItems.item_id == item_id)
                .order_by(ProducedItems.created_at.asc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_item_id_paginated(item_id: str, page: int, page_size: int) -> tuple[list[ProducedItems], int]:
        offset = (page - 1) * page_size
        async with db_manager.session_factory() as db:
            total = int(
                await db.scalar(
                    select(func.count()).select_from(ProducedItems).where(ProducedItems.item_id == item_id)
                )
                or 0
            )
            result = await db.execute(
                select(ProducedItems)
                .where(ProducedItems.item_id == item_id)
                .order_by(ProducedItems.created_at.asc())
                .offset(offset)
                .limit(page_size)
            )
            return list(result.scalars().all()), total
