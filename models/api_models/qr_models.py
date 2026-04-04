"""Pydantic API models for QR Code endpoints."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


from uuid import UUID

class QRCodeCreateRequest(BaseModel):
    """Request body for creating a QR code."""

    id: str = Field(
        ..., 
        min_length=8, 
        max_length=8, 
        pattern=r"^\d{8}$", 
        description="The unique physical ID of the QR Code (must be exactly 8 digits)"
    )
    notes: str | None = None


class QRCodeStatusUpdate(BaseModel):
    """Request body for updating a QR code status."""

    notes: str | None = None


class QRTagStatusUpdate(BaseModel):
    """Request body for updating a QR code via PUT."""

    status: str
    notes: str | None = None


class QRCodeToggleRequest(BaseModel):
    """Request body for enabling/disabling a QR code by ids."""

    user_id: UUID
    qr_code_id: str = Field(..., min_length=1)
    notes: str | None = None


class QRCodeResponse(BaseModel):
    """Public QR Code response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    registered_by: UUID | str
    enabled_by: UUID | str | None
    enabled_at: datetime | None
    disabled_by: UUID | str | None
    disabled_at: datetime | None
    created_at: datetime | None
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