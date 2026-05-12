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
            name=payload.name,
            sequence_order=payload.sequence_order,
            status=payload.status,
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
        if payload.name is not None:
            update_data["name"] = payload.name
        if payload.sequence_order is not None:
            update_data["sequence_order"] = payload.sequence_order
        if payload.status is not None:
            update_data["status"] = payload.status


        updated_department = await DepartmentDBHandler.update(department_id, update_data)
        if updated_department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        return updated_department

    @staticmethod
    async def delete_department(department_id: UUID) -> None:
        deleted = await DepartmentDBHandler.delete(department_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )
