"""Pydantic API models for produced items endpoints."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProducedItemResponse(BaseModel):
    """Public produced item response model."""

    model_config = ConfigDict(from_attributes=True)

    produced_id: str
    qr_id: str
    item_id: str
    department_name: str
    general_remarks: str | None
    issue_remarks: str | None
    created_by: str | None
    updated_by: str | None
    remark_by: str | None
    remark_updated: str | None
    created_at: datetime


class ProducedItemsPaginatedResponse(BaseModel):
    """Paginated grouped produced-items response."""

    items: dict[str, list[ProducedItemResponse]]
    page: int
    page_size: int
    total: int
    total_pages: int


class ProducedItemsGroupedResponse(BaseModel):
    """Non-paginated grouped produced-items response."""

    items: dict[str, list[ProducedItemResponse]]


class ProductionHistoryItem(BaseModel):
    """Single production history record (aggregated by item_id)."""
    id: str
    qr_id: str
    batch_number: str | None
    product_name: str | None
    remarks_data: list[ProducedItemResponse]
    activated_by: str | None
    activated_at: datetime | None
    released_by: str | None
    released_at: datetime | None
    total_departments: int
    departments_with_issues: int
    created_at: datetime | None


class ProductionHistoryPaginatedResponse(BaseModel):
    """Paginated production history response."""
    items: list[ProductionHistoryItem]
    total: int
    page: int
    size: int
    pages: int
