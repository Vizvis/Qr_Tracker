"""Global error response models for API exceptions."""
from datetime import datetime
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard API error payload for all endpoints."""

    success: bool = False
    error_type: str
    detail: str
    path: str
    timestamp: datetime
    trace: list[str] | None = None
