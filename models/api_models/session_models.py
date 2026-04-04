"""Pydantic API models for session and remarks endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class SessionRemarkCreateRequest(BaseModel):
    """Payload for creating a department remark in an active QR session."""

    item_id: str = Field(..., min_length=1, max_length=120)
    department_id: UUID
    general_remarks: str | None = Field(default=None, max_length=1000)
    issue_remarks: str | None = Field(default=None, max_length=1000)
    custom_data: dict | None = Field(default_factory=dict)

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
        return value.strip()

    @model_validator(mode="after")
    def ensure_any_remark_present(self):
        has_general = self.general_remarks is not None
        has_issue = self.issue_remarks is not None
        has_custom = bool(self.custom_data)
        if not has_general and not has_issue and not has_custom:
            raise ValueError("At least one of general_remarks, issue_remarks, or custom_data is required.")
        return self


class SessionRemarkUpdateRequest(BaseModel):
    """Payload for updating a remark in an active QR session."""

    general_remarks: str = Field(default="", max_length=1000)
    issue_remarks: str = Field(default="", max_length=1000)  # empty string clears the error flag


class SessionRemarkResponse(BaseModel):
    """Response payload for a remark row."""
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    id: str
    qr_id: str
    item_id: str
    department_id: str | None
    department: str | None
    general_remarks: str | None
    issue_remarks: str | None
    custom_data: dict | None = Field(default_factory=dict)
    remarks_history: list[dict] | None = Field(default_factory=list)
    remark_by: str | None
    remark_updated: str | None
    created_at: datetime | None
    updated_at: datetime | None

class ActiveQRRemarksResponse(BaseModel):
    """Response payload for active QR and their session remarks."""
    model_config = ConfigDict(ser_json_timedelta='iso8601')

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
