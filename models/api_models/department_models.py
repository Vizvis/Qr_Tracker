"""Pydantic API models for department endpoints."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from models.db_models.enums import DepartmentEnum, DepartmentStatus


class DepartmentCreateRequest(BaseModel):
    """Request body for creating a department."""

    dept_type: DepartmentEnum
    status: DepartmentStatus = DepartmentStatus.ACTIVE
    head_of_department: UUID | None = None


class DepartmentUpdateRequest(BaseModel):
    """Request body for updating a department."""

    dept_type: DepartmentEnum | None = None
    status: DepartmentStatus | None = None
    head_of_department: UUID | None = None


class DepartmentResponse(BaseModel):
    """Public department response model."""

    id: str
    dept_type: DepartmentEnum
    status: DepartmentStatus
    head_of_department: str | None
    created_on: datetime
