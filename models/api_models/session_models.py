"""Pydantic API models for session and remarks endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class SessionRemarkCreateRequest(BaseModel):
    """Payload for creating a department remark in an active QR session."""

    item_id: str = Field(..., min_length=1, max_length=120)
    department_id: UUID
    general_remarks: str | None = Field(default=None, max_length=1000)
    issue_remarks: str | None = Field(default=None, max_length=1000)

    @field_validator("item_id")
    @classmethod
    def validate_item_id(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("item_id cannot be empty.")
        return trimmed

    @field_validator("general_remarks", "issue_remarks")
    @classmethod
    def normalize_optional_remarks(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def ensure_any_remark_present(self):
        if not self.general_remarks and not self.issue_remarks:
            raise ValueError("At least one of general_remarks or issue_remarks is required.")
        return self


class SessionRemarkResponse(BaseModel):
    """Response payload for a remark row."""

    id: str
    qr_id: str
    item_id: str
    department_id: str | None
    department: str | None
    general_remarks: str | None
    issue_remarks: str | None
    remark_by: str | None
    remark_updated: str | None
    created_at: datetime | None


class ActiveQRRemarksResponse(BaseModel):
    """Response payload for active QR and their session remarks."""

    qr_id: str
    status: str
    enabled_at: datetime | None
    notes: str | None
    remarks: list[SessionRemarkResponse]


class ActiveQRRemarksListResponse(BaseModel):
    """Paginated active QR remarks response payload."""

    items: list[ActiveQRRemarksResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
    count: int
    active_qrs: list[ActiveQRRemarksResponse]
