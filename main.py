"""
Main FastAPI application entry point.
"""
from datetime import datetime
import traceback
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from auth.cookie_auth import require_valid_auth_cookie
from db_handler.database import db_manager
from core.routes.user_route import user_router
from core.routes.department_route import department_router
from core.routes.qr_route import qr_router
from models.api_models.error_models import ErrorResponse


ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    403: {"model": ErrorResponse, "description": "Forbidden"},
    404: {"model": ErrorResponse, "description": "Not Found"},
    409: {"model": ErrorResponse, "description": "Conflict"},
    422: {"model": ErrorResponse, "description": "Validation Error"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
}

# Initialize FastAPI app
app = FastAPI(
    title="QR Tracker API",
    description="QR Code tracking and production session management system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    responses=ERROR_RESPONSES,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(user_router)
app.include_router(department_router)
app.include_router(qr_router)


def _format_validation_detail(errors: list[dict]) -> str:
    """Convert Pydantic validation errors into a concise readable string."""
    parts = []
    for err in errors:
        loc = ".".join(str(item) for item in err.get("loc", []))
        msg = err.get("msg", "Invalid input")
        if loc:
            parts.append(f"{loc}: {msg}")
        else:
            parts.append(msg)
    return "; ".join(parts)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return a consistent error payload for all HTTP exceptions."""
    payload = ErrorResponse(
        error_type="HTTPException",
        detail=str(exc.detail),
        path=request.url.path,
        timestamp=datetime.utcnow(),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return detailed validation errors with a consistent payload."""
    detail = _format_validation_detail(exc.errors())
    payload = ErrorResponse(
        error_type="ValidationError",
        detail=detail,
        path=request.url.path,
        timestamp=datetime.utcnow(),
    )
    return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return detailed unhandled exception payload."""
    payload = ErrorResponse(
        error_type=exc.__class__.__name__,
        detail=str(exc),
        path=request.url.path,
        timestamp=datetime.utcnow(),
        trace=traceback.format_exception(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))


# Health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check(_: Annotated[dict, Depends(require_valid_auth_cookie)]):
    """Health check endpoint to verify API is running."""
    return {
        "status": "healthy",
        "message": "QR Tracker API is running",
        "service": "QR Tracker API v1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root(_: Annotated[dict, Depends(require_valid_auth_cookie)]):
    """Root endpoint with API information."""
    return {
        "message": "Welcome to QR Tracker API",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/api/health"
    }


# Startup event
@app.on_event("startup")
async def startup():
    """Event triggered on application startup."""
    print("Starting QR Tracker API...")
    print("Database connection initialized")


# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    """Event triggered on application shutdown."""
    print("Shutting down QR Tracker API...")
    await db_manager.close()
    print("Database connection closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
