"""Pydantic API models for produced items endpoints."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProducedItemResponse(BaseModel):
    """Public produced item response model."""

    model_config = ConfigDict(from_attributes=True)

    produced_id: str
    qr_id: str
    item_id: str
    department_id: str
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
