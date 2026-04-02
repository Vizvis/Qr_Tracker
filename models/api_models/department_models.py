"""Pydantic API models for department endpoints."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from models.db_models.enums import DepartmentStatus


class DepartmentCreateRequest(BaseModel):
    """Request body for creating a department."""

    name: str
    sequence_order: int = 0
    status: DepartmentStatus = DepartmentStatus.ACTIVE
    head_of_department: UUID | None = None


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
    created_on: datetime


class DepartmentListResponse(BaseModel):
    """Paginated department list response payload."""

    items: list[DepartmentResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
