"""
Database configuration for local and cloud environments.
Default is cloud (USE_LOCAL_DB=False), set to True for local development.
"""
import os
import secrets

# Environment control
USE_LOCAL_DB = True

# Cloud Database (Supabase)
DB_USER_CLOUD = "postgres"
DB_PASSWORD_CLOUD = ""
DB_HOST_CLOUD = ""
DB_PORT_CLOUD = 5432
DB_NAME_CLOUD = "postgres"

# Local Database (PostgreSQL)
DB_USER_LOCAL = "postgres"
DB_PASSWORD_LOCAL = "sivu%402004"
DB_HOST_LOCAL = "localhost"
DB_PORT_LOCAL = 5432
DB_NAME_LOCAL = "QR_tracker"

# JWT Settings
# Prefer environment-provided key; fallback to a random dev key when missing.
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class DatabaseConfig:
    """Database configuration helper class."""
    
    @staticmethod
    def get_database_url() -> str:
        """Returns database URL based on environment setting."""
        if USE_LOCAL_DB:
            return (
                f"postgresql+asyncpg://{DB_USER_LOCAL}:"
                f"{DB_PASSWORD_LOCAL}@{DB_HOST_LOCAL}:"
                f"{DB_PORT_LOCAL}/{DB_NAME_LOCAL}"
            )
        else:
            return (
                f"postgresql+asyncpg://{DB_USER_CLOUD}:"
                f"{DB_PASSWORD_CLOUD}@{DB_HOST_CLOUD}:"
                f"{DB_PORT_CLOUD}/{DB_NAME_CLOUD}"
            )

    @staticmethod
    def get_database_url_sync() -> str:
        """Returns synchronous database URL for Alembic migrations."""
        if USE_LOCAL_DB:
            return (
                f"postgresql://{DB_USER_LOCAL}:"
                f"{DB_PASSWORD_LOCAL}@{DB_HOST_LOCAL}:"
                f"{DB_PORT_LOCAL}/{DB_NAME_LOCAL}"
            )
        else:
            return (
                f"postgresql://{DB_USER_CLOUD}:"
                f"{DB_PASSWORD_CLOUD}@{DB_HOST_CLOUD}:"
                f"{DB_PORT_CLOUD}/{DB_NAME_CLOUD}"
            )
