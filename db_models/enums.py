"""Enums for database models."""
from enum import Enum


class RoleLevel(str, Enum):
    """User role levels."""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    OPERATOR = "operator"
    VIEWER = "viewer"


class DepartmentEnum(str, Enum):
    """Department types."""
    PRODUCTION = "production"
    QUALITY_ASSURANCE = "quality_assurance"
    PACKAGING = "packaging"
    SHIPPING = "shipping"
    WAREHOUSE = "warehouse"
    MANAGEMENT = "management"
