"""Pydantic API models for QR Code endpoints."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


from uuid import UUID

class QRCodeCreateRequest(BaseModel):
    """Request body for creating a QR code."""

    id: str = Field(..., min_length=1, description="The unique physical ID of the QR Code")
    notes: str | None = None


class QRCodeStatusUpdate(BaseModel):
    """Request body for updating a QR code status."""
    
    notes: str | None = None


class QRCodeResponse(BaseModel):
    """Public QR Code response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    registered_by: UUID
    enabled_by: UUID | None
    enabled_at: datetime | None
    created_at: datetime
    notes: str | None


class QRSessionFinalizeResponse(BaseModel):
    """Response payload for moving remarks into produced_items and clearing remarks."""

    qr_id: str
    moved_count: int
    message: str


class QRCodeListResponse(BaseModel):
    """Paginated QR code list response payload."""

    items: list[QRCodeResponse]
    page: int
    page_size: int
    total: int
    total_pages: int