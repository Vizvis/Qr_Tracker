"""Department API routes for create and update operations."""
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Query, status
from auth.cookie_auth import require_valid_auth_cookie
from core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from core.services.department_service import DepartmentService
from models.api_models.department_models import (
    DepartmentCreateRequest,
    DepartmentUpdateRequest,
    DepartmentResponse,
    DepartmentListResponse,
)


department_router = APIRouter(prefix="/api/departments", tags=["Departments"])


def _to_department_response(department) -> DepartmentResponse:
    return DepartmentResponse(
        id=str(department.id),
        name=department.name,
        sequence_order=department.sequence_order,
        status=department.status,
        head_of_department=str(department.head_of_department) if department.head_of_department else None,
        created_on=department.created_on,
    )


@department_router.get("", response_model=DepartmentListResponse)
async def get_departments(
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
):
    """Get all departments endpoint."""
    result = await DepartmentService.get_departments(page, page_size)
    result["items"] = [_to_department_response(department) for department in result["items"]]
    return result


@department_router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreateRequest,
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Create department endpoint."""
    department = await DepartmentService.create_department(payload)
    return _to_department_response(department)


@department_router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: Annotated[UUID, Path(..., description="Department ID")],
    payload: DepartmentUpdateRequest,
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Update department endpoint including active/inactive status."""
    department = await DepartmentService.update_department(department_id, payload)
    return _to_department_response(department)

@department_router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: Annotated[UUID, Path(..., description="Department ID")],
    _: Annotated[dict, Depends(require_valid_auth_cookie)],
):
    """Delete a department by ID."""
    await DepartmentService.delete_department(department_id)

