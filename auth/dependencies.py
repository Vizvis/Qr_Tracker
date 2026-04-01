"""FastAPI dependencies for role-based access control."""
from fastapi import Depends, HTTPException, status, Request
from auth.cookie_auth import CookieAuth
from auth.jwt_auth import JWTAuth
from models.db_models.enums import RoleLevel
from uuid import UUID


ROLE_PRIORITY: dict[str, int] = {
    RoleLevel.VIEWER.value: 1,
    RoleLevel.OPERATOR.value: 2,
    RoleLevel.SUPERVISOR.value: 3,
    RoleLevel.ADMIN.value: 4,
}

ROLE_ALIASES: dict[str, str] = {
    "admin": RoleLevel.ADMIN.value,
    "super": RoleLevel.SUPERVISOR.value,
    "supervisor": RoleLevel.SUPERVISOR.value,
    "superviro": RoleLevel.SUPERVISOR.value,
    "operator": RoleLevel.OPERATOR.value,
    "viewer": RoleLevel.VIEWER.value,
}


def _normalize_role(raw_role: str) -> str:
    """Normalize role strings from token payloads into canonical names."""
    role_value = raw_role.split(".")[-1].strip().lower()
    return ROLE_ALIASES.get(role_value, role_value)


def _require_min_role(min_role: str):
    """Dependency factory enforcing role hierarchy by minimum role."""
    normalized_min_role = _normalize_role(min_role)
    min_priority = ROLE_PRIORITY.get(normalized_min_role)
    if min_priority is None:
        raise ValueError(f"Invalid minimum role configured: {min_role}")

    def role_checker(payload: dict = Depends(get_current_user_token)) -> UUID:
        try:
            role_param = str(payload.get("role", ""))
            normalized_role = _normalize_role(role_param)
            role_priority = ROLE_PRIORITY.get(normalized_role)

            if role_priority is None or role_priority < min_priority:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"Insufficient permissions. Required minimum role: {normalized_min_role}"
                    ),
                )

            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload.",
                )

            return UUID(user_id)
        except (ValueError, KeyError, AttributeError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid role in token payload.",
            ) from e

    return role_checker

def get_current_user_token(request: Request) -> dict:
    """Validate access token from cookie and return JWT payload."""
    token = CookieAuth.get_token_from_cookie(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login first.",
        )

    payload = JWTAuth.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    return payload

def require_role(allowed_roles: list[str]):
    """Dependency factory for checking if user has required role."""
    def role_checker(payload: dict = Depends(get_current_user_token)) -> UUID:
        try:
            role_param = str(payload.get("role", ""))
            normalized_role = _normalize_role(role_param)
            normalized_allowed_roles = {_normalize_role(role) for role in allowed_roles}

            if normalized_role not in normalized_allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Allowed roles: {', '.join(allowed_roles)}"
                )

            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload."
                )
            
            return UUID(user_id)
        except (ValueError, KeyError, AttributeError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid role in token payload."
            ) from e

    return role_checker

require_admin = _require_min_role(RoleLevel.ADMIN.value)
require_supervisor = _require_min_role(RoleLevel.SUPERVISOR.value)
require_super = require_supervisor
require_superviro = require_supervisor
require_operator = _require_min_role(RoleLevel.OPERATOR.value)
require_viewer = _require_min_role(RoleLevel.VIEWER.value)
