"""Cookie-based authentication handler for FastAPI."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Response, Request
from config import ACCESS_TOKEN_EXPIRE_MINUTES


class CookieAuth:
    """Cookie-based authentication handler."""
    
    COOKIE_NAME = "access_token"
    REFRESH_COOKIE_NAME = "refresh_token"
    
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
        response.delete_cookie(
            key=CookieAuth.COOKIE_NAME,
            httponly=True,
            samesite="lax",
        )
        response.delete_cookie(
            key=CookieAuth.REFRESH_COOKIE_NAME,
            httponly=True,
            samesite="lax",
        )
