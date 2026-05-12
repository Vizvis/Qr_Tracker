"""
Database configuration for local and GCP Cloud SQL environments.
All sensitive values are loaded from environment variables / .env file.
"""
import os
from urllib.parse import quote
from dotenv import load_dotenv

# Load .env file (does nothing if file doesn't exist)
load_dotenv()

# Environment control
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "true").lower() == "true"

# Cloud Database (Supabase)
DB_USER_CLOUD = os.getenv("DB_USER_CLOUD", "postgres")
DB_PASSWORD_CLOUD = os.getenv("DB_PASSWORD_CLOUD", "")
DB_HOST_CLOUD = os.getenv("DB_HOST_CLOUD", "")
DB_PORT_CLOUD = int(os.getenv("DB_PORT_CLOUD", "5432"))
DB_NAME_CLOUD = os.getenv("DB_NAME_CLOUD", "postgres")

# Local Database (PostgreSQL)
DB_USER_LOCAL = os.getenv("DB_USER", "postgres")
DB_PASSWORD_LOCAL = os.getenv("DB_PASSWORD", "")
DB_HOST_LOCAL = os.getenv("DB_HOST", "localhost")
DB_PORT_LOCAL = int(os.getenv("DB_PORT", "5432"))
DB_NAME_LOCAL = os.getenv("DB_NAME", "QR_tracker")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set! "
        "Set it in your .env file or as a system environment variable."
    )
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database connection pool settings
# pool_size: number of persistent connections kept open
# max_overflow: extra connections allowed above pool_size under burst load
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))

# SSL mode for cloud DB: 'require' | 'disable'
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "require")

# CORS Origins (comma-separated list)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "https://frontend-qvoy.vercel.app,http://localhost:5173").split(",")
    if origin.strip()
]


class DatabaseConfig:
    """Database configuration helper class."""
    
    @staticmethod
    def get_database_url() -> str:
        """Returns async database URL based on environment setting."""
        if USE_LOCAL_DB:
            return (
                f"postgresql+asyncpg://{DB_USER_LOCAL}:"
                f"{quote(DB_PASSWORD_LOCAL, safe='')}@{DB_HOST_LOCAL}:"
                f"{DB_PORT_LOCAL}/{DB_NAME_LOCAL}"
            )
        else:
            # GCP Cloud SQL via public IP — SSL handled via connect_args in database.py
            return (
                f"postgresql+asyncpg://{DB_USER_CLOUD}:"
                f"{quote(DB_PASSWORD_CLOUD, safe='')}@{DB_HOST_CLOUD}:"
                f"{DB_PORT_CLOUD}/{DB_NAME_CLOUD}"
            )

    @staticmethod
    def get_database_url_sync() -> str:
        """Returns synchronous database URL for Alembic migrations."""
        if USE_LOCAL_DB:
            return (
                f"postgresql://{DB_USER_LOCAL}:"
                f"{quote(DB_PASSWORD_LOCAL, safe='')}@{DB_HOST_LOCAL}:"
                f"{DB_PORT_LOCAL}/{DB_NAME_LOCAL}"
            )
        else:
            # GCP Cloud SQL via public IP (psycopg2 uses sslmode=require)
            ssl_suffix = "?sslmode=require" if DB_SSL_MODE == "require" else ""
            return (
                f"postgresql://{DB_USER_CLOUD}:"
                f"{quote(DB_PASSWORD_CLOUD, safe='')}@{DB_HOST_CLOUD}:"
                f"{DB_PORT_CLOUD}/{DB_NAME_CLOUD}{ssl_suffix}"
            )
