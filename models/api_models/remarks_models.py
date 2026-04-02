"""Pydantic API models for remark CRUD endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class RemarkCreateRequest(BaseModel):
    """Request body for creating a remark."""

    qr_id: str = Field(..., min_length=1, max_length=120)
    item_id: str = Field(..., min_length=1, max_length=120)
    department_id: UUID
    general_remarks: str | None = Field(default=None, max_length=1000)
    issue_remarks: str | None = Field(default=None, max_length=1000)

    @field_validator("qr_id", "item_id")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Value cannot be empty.")
        return trimmed

    @field_validator("general_remarks", "issue_remarks")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def require_some_remark(self):
        if not self.general_remarks and not self.issue_remarks:
            raise ValueError("At least one remark field is required.")
        return self


class RemarkUpdateRequest(BaseModel):
    """Request body for patching a remark."""

    item_id: str | None = Field(default=None, min_length=1, max_length=120)
    department_id: UUID | None = None
    general_remarks: str | None = Field(default=None, max_length=1000)
    issue_remarks: str | None = Field(default=None, max_length=1000)

    @field_validator("item_id")
    @classmethod
    def trim_optional_item_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @field_validator("general_remarks", "issue_remarks")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def require_any_field(self):
        if (
            self.item_id is None
            and self.department_id is None
            and self.general_remarks is None
            and self.issue_remarks is None
        ):
            raise ValueError("At least one field is required for update.")
        return self


class RemarkResponse(BaseModel):
    """Public remark response model."""

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


class RemarkListResponse(BaseModel):
    """Paginated remark list response payload."""

    items: list[RemarkResponse]
    page: int
    page_size: int
    total: int
    total_pages: int