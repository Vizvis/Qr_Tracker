"""FastAPI dependencies for role-based access control."""
from fastapi import Depends, HTTPException, status, Request
from auth.cookie_auth import CookieAuth
from auth.jwt_auth import JWTAuth
from models.db_models.enums import RoleLevel
from uuid import UUID

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
            role_param = payload.get("role", "")
            
            # Support both string payload ('admin') or Enum string representation ('RoleLevel.ADMIN')
            role_val = role_param.split(".")[-1].lower()
                
            if role_val not in allowed_roles:
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

require_admin = require_role(["admin"])
require_supervisor = require_role(["admin", "supervisor"])
require_operator = require_role(["admin", "supervisor", "operator"])
