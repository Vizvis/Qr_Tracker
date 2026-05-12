"""Pydantic API models for session and remarks endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class SessionRemarkCreateRequest(BaseModel):
    """Payload for creating a department remark in an active QR session."""

    item_id: str = Field(..., min_length=1, max_length=8, pattern=r"^\d{1,8}$")
    department_id: UUID
    field_1: int | None = Field(default=None, ge=0)
    field_2: int | None = Field(default=None, ge=0)
    field_3: int | None = Field(default=None, ge=0)
    field_4: int | None = Field(default=None, ge=0)
    field_5: int | None = Field(default=None, ge=0)
    issue_remarks: str | None = Field(default=None, max_length=1000)
    custom_data: dict | None = Field(default_factory=dict)

    @field_validator("item_id")
    @classmethod
    def validate_item_id(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("item_id cannot be empty.")
        return trimmed

    @field_validator("issue_remarks")
    @classmethod
    def normalize_optional_remarks(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def ensure_any_data_present(self):
        has_fields = any(
            getattr(self, f"field_{i}") is not None for i in range(1, 6)
        )
        has_issue = self.issue_remarks is not None
        has_custom = bool(self.custom_data)
        if not has_fields and not has_issue and not has_custom:
            raise ValueError("At least one of field_1..5, issue_remarks, or custom_data is required.")
        return self


class SessionRemarkUpdateRequest(BaseModel):
    """Payload for updating a remark in an active QR session."""

    field_1: int | None = Field(default=None, ge=0)
    field_2: int | None = Field(default=None, ge=0)
    field_3: int | None = Field(default=None, ge=0)
    field_4: int | None = Field(default=None, ge=0)
    field_5: int | None = Field(default=None, ge=0)
    issue_remarks: str = Field(default="", max_length=1000)  # empty string clears the error flag


class SessionRemarkResponse(BaseModel):
    """Response payload for a remark row."""
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    id: str
    qr_id: str
    item_id: str
    department_id: str | None
    department: str | None
    field_1: int | None = 0
    field_2: int | None = 0
    field_3: int | None = 0
    field_4: int | None = 0
    field_5: int | None = 0
    issue_remarks: str | None
    custom_data: dict | None = Field(default_factory=dict)
    remarks_history: list[dict] | None = Field(default_factory=list)
    scanned_by: str | None
    last_edited_by: str | None
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
