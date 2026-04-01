"""Cookie-based authentication handler for FastAPI."""
from typing import Optional
from fastapi import HTTPException, Response, Request, status
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from auth.jwt_auth import JWTAuth


class CookieAuth:
    """Cookie-based authentication handler."""
    
    COOKIE_NAME = "access_token"
    REFRESH_COOKIE_NAME = "refresh_token"
    COOKIE_PATH = "/"
    
    @staticmethod
    def set_auth_cookie(response: Response, token: str, max_age: Optional[int] = None) -> None:
        """Set authentication cookie in response."""
        if max_age is None:
            max_age = ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        response.set_cookie(
            key=CookieAuth.COOKIE_NAME,
            value=token,
            max_age=max_age,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path=CookieAuth.COOKIE_PATH,
        )
    
    @staticmethod
    def set_refresh_cookie(response: Response, token: str) -> None:
        """Set refresh token cookie in response."""
        response.set_cookie(
            key=CookieAuth.REFRESH_COOKIE_NAME,
            value=token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path=CookieAuth.COOKIE_PATH,
        )
    
    @staticmethod
    def get_token_from_cookie(request: Request) -> Optional[str]:
        """Extract access token from cookie."""
        return request.cookies.get(CookieAuth.COOKIE_NAME)
    
    @staticmethod
    def get_refresh_token_from_cookie(request: Request) -> Optional[str]:
        """Extract refresh token from cookie."""
        return request.cookies.get(CookieAuth.REFRESH_COOKIE_NAME)
    
    @staticmethod
    def delete_auth_cookies(response: Response) -> None:
        """Delete authentication cookies from response."""
        # Delete current cookie path.
        response.delete_cookie(
            key=CookieAuth.COOKIE_NAME,
            httponly=True,
            samesite="lax",
            path=CookieAuth.COOKIE_PATH,
        )
        response.delete_cookie(
            key=CookieAuth.REFRESH_COOKIE_NAME,
            httponly=True,
            samesite="lax",
            path=CookieAuth.COOKIE_PATH,
        )

        # Cleanup legacy cookies that may have been set under /api path.
        response.delete_cookie(
            key=CookieAuth.COOKIE_NAME,
            httponly=True,
            samesite="lax",
            path="/api",
        )
        response.delete_cookie(
            key=CookieAuth.REFRESH_COOKIE_NAME,
            httponly=True,
            samesite="lax",
            path="/api",
        )


async def require_valid_auth_cookie(request: Request) -> dict:
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
