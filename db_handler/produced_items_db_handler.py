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

    @staticmethod
    async def search_production_history(
        search: str | None, start_date: str | None, end_date: str | None, page: int, page_size: int
    ) -> tuple[list[ProducedItems], int]:
        from sqlalchemy import or_, distinct
        offset = (page - 1) * page_size
        async with db_manager.session_factory() as db:
            query = select(ProducedItems.item_id).distinct()

            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        ProducedItems.qr_id.ilike(search_term),
                        ProducedItems.item_id.ilike(search_term),
                        ProducedItems.department_name.ilike(search_term),
                        ProducedItems.general_remarks.ilike(search_term),
                        ProducedItems.issue_remarks.ilike(search_term)
                    )
                )

            if start_date:
                query = query.where(ProducedItems.created_at >= start_date)
            if end_date:
                query = query.where(ProducedItems.created_at <= end_date)

            # Count total distinct item_ids matching the criteria
            count_query = select(func.count(distinct(ProducedItems.item_id))).select_from(query.subquery())
            total = int(await db.scalar(count_query) or 0)

            if total == 0:
                return [], 0

            # Get the page of item_ids
            paginated_item_ids_result = await db.execute(
                query.offset(offset).limit(page_size)
            )
            item_ids = paginated_item_ids_result.scalars().all()

            # Now fetch all rows for these item_ids
            rows_result = await db.execute(
                select(ProducedItems)
                .where(ProducedItems.item_id.in_(item_ids))
                .order_by(ProducedItems.created_at.desc())
            )
            return list(rows_result.scalars().all()), total
