"""
Database engine and session management with Singleton pattern.
"""
import ssl
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from config import DatabaseConfig, DB_POOL_SIZE, DB_MAX_OVERFLOW, USE_LOCAL_DB


class DatabaseManager:
    """Singleton class for database connection management."""

    _instance: Optional["DatabaseManager"] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[sessionmaker] = None

    def __new__(cls) -> "DatabaseManager":
        """Ensure only one instance of DatabaseManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the database engine and session factory."""
        if self._engine is None:
            # asyncpg requires SSL to be passed as an SSLContext object,
            # not as a URL query parameter (?ssl=require is silently ignored).
            connect_args = {}
            if not USE_LOCAL_DB:
                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE
                connect_args["ssl"] = ssl_ctx

            self._engine = create_async_engine(
                DatabaseConfig.get_database_url(),
                echo=False,
                future=True,
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                connect_args=connect_args,
                # Recycle connections after 30 min to stay ahead of GCP's idle
                # connection timeout, which silently drops connections server-side.
                pool_recycle=1800,
            )

            self._session_factory = sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine."""
        if self._engine is None:
            self._initialize()
        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        """Get the session factory."""
        if self._session_factory is None:
            self._initialize()
        return self._session_factory

    async def get_session(self) -> AsyncSession:
        """Create a new database session."""
        async with self.session_factory() as session:
            return session

    async def close(self) -> None:
        """Close the database connection."""
        if self._engine is not None:
            await self._engine.dispose()


# Reset singleton on each module import so uvicorn --reload gets a fresh engine.
DatabaseManager._instance = None
DatabaseManager._engine = None
DatabaseManager._session_factory = None

# Singleton instance — created fresh on every module load
db_manager = DatabaseManager()


async def get_db():
    """Dependency for FastAPI to get database session."""
    async with db_manager.session_factory() as session:
        yield session


# Lazy accessors — resolve against the live db_manager, not a cached object
def get_engine() -> AsyncEngine:
    return db_manager.engine


def get_session_factory() -> sessionmaker:
    return db_manager.session_factory


# Backward-compatible aliases
engine = db_manager.engine
AsyncSessionLocal = db_manager.session_factory
