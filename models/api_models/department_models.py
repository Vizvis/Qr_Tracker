"""Pydantic API models for department endpoints."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator
from models.db_models.enums import DepartmentEnum, DepartmentStatus


class DepartmentCreateRequest(BaseModel):
    """Request body for creating a department."""

    name: DepartmentEnum
    sequence_order: int = 0
    status: DepartmentStatus = DepartmentStatus.ACTIVE
    head_of_department: UUID | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        if isinstance(value, DepartmentEnum):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            for department in DepartmentEnum:
                if department.value == normalized:
                    return department
        allowed = ", ".join(item.value for item in DepartmentEnum)
        raise ValueError(f"Invalid department name. Allowed values: {allowed}")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        if isinstance(value, DepartmentStatus):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            for status in DepartmentStatus:
                if status.value == normalized:
                    return status
        allowed = ", ".join(item.value for item in DepartmentStatus)
        raise ValueError(f"Invalid status. Allowed values: {allowed}")


class DepartmentUpdateRequest(BaseModel):
    """Request body for updating a department."""

    name: str | None = None
    sequence_order: int | None = None
    status: DepartmentStatus | None = None
    head_of_department: UUID | None = None


class DepartmentResponse(BaseModel):
    """Public department response model."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    sequence_order: int
    status: DepartmentStatus
    head_of_department: str | None
    created_on: datetime | None


class DepartmentListResponse(BaseModel):
    """Paginated department list response payload."""

    items: list[DepartmentResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
