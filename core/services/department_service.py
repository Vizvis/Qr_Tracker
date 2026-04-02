"""Department service layer for business logic workflows."""
from uuid import UUID
from fastapi import HTTPException, status
from core.pagination import build_pagination, normalize_page_size
from db_handler.department_db_handler import DepartmentDBHandler
from models.db_models.department import Department
from models.api_models.department_models import DepartmentCreateRequest, DepartmentUpdateRequest


class DepartmentService:
    """Business logic for department endpoints."""

    @staticmethod
    async def get_departments(page: int, page_size: int) -> dict:
        normalized_page_size = normalize_page_size(page_size)
        departments, total = await DepartmentDBHandler.list_paginated(page, normalized_page_size)
        return {
            "items": departments,
            **build_pagination(page, normalized_page_size, total),
        }

    @staticmethod
    async def get_department_by_id(department_id: UUID) -> Department:
        department = await DepartmentDBHandler.get_by_id(department_id)
        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )
        return department

    @staticmethod
    async def create_department(payload: DepartmentCreateRequest) -> Department:
        department = Department(
            dept_type=payload.dept_type,
            status=payload.status,
            head_of_department=payload.head_of_department,
        )
        return await DepartmentDBHandler.create(department)

    @staticmethod
    async def update_department(department_id: UUID, payload: DepartmentUpdateRequest) -> Department:
        existing = await DepartmentDBHandler.get_by_id(department_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        update_data = {}
        if payload.dept_type is not None:
            update_data["dept_type"] = payload.dept_type
        if payload.status is not None:
            update_data["status"] = payload.status
        if "head_of_department" in payload.model_fields_set:
            update_data["head_of_department"] = payload.head_of_department

        updated_department = await DepartmentDBHandler.update(department_id, update_data)
        if updated_department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        return updated_department
