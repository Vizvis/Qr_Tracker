"""Pydantic API models for remark CRUD endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

class RemarkCreateRequest(BaseModel):
    """Request body for creating a remark."""

    qr_id: str = Field(..., min_length=1, max_length=120)
    item_id: str = Field(..., min_length=1, max_length=8, pattern=r"^\d{1,8}$")
    department_id: UUID
    field_1: int | None = Field(default=None, ge=0)
    field_2: int | None = Field(default=None, ge=0)
    field_3: int | None = Field(default=None, ge=0)
    field_4: int | None = Field(default=None, ge=0)
    field_5: int | None = Field(default=None, ge=0)
    issue_remarks: str | None = Field(default=None, max_length=1000)
    custom_data: dict | None = Field(default_factory=dict)

    @field_validator("qr_id", "item_id")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Value cannot be empty.")
        return trimmed

    @field_validator("issue_remarks")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def require_some_data(self):
        has_fields = any(
            getattr(self, f"field_{i}") is not None for i in range(1, 6)
        )
        has_issue = self.issue_remarks is not None
        has_custom = bool(self.custom_data)
        if not has_fields and not has_issue and not has_custom:
            raise ValueError("At least one field value, issue_remarks, or custom_data is required.")
        return self


class RemarkUpdateRequest(BaseModel):
    """Request body for patching a remark."""

    item_id: str | None = Field(default=None, min_length=1, max_length=120)
    department_id: UUID | None = None
    field_1: int | None = Field(default=None, ge=0)
    field_2: int | None = Field(default=None, ge=0)
    field_3: int | None = Field(default=None, ge=0)
    field_4: int | None = Field(default=None, ge=0)
    field_5: int | None = Field(default=None, ge=0)
    issue_remarks: str | None = Field(default=None, max_length=1000)
    custom_data: dict | None = None

    @field_validator("item_id")
    @classmethod
    def trim_optional_item_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed

    @field_validator("issue_remarks")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def require_any_field(self):
        if (
            self.item_id is None
            and self.department_id is None
            and all(getattr(self, f"field_{i}") is None for i in range(1, 6))
            and self.issue_remarks is None
            and self.custom_data is None
        ):
            raise ValueError("At least one field is required for update.")
        return self


class RemarkResponse(BaseModel):
    """Public remark response model."""
    
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
    remark_by: str | None
    remark_updated: str | None
    created_at: datetime | None
    updated_at: datetime | None


class RemarkListResponse(BaseModel):
    """Paginated remark list response payload."""

    items: list[RemarkResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
