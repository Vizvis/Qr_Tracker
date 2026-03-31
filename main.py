"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_handler import db_manager

# Initialize FastAPI app
app = FastAPI(
    title="QR Tracker API",
    description="QR Code tracking and production session management system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify API is running."""
    return {
        "status": "healthy",
        "message": "QR Tracker API is running",
        "service": "QR Tracker API v1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
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
