"""
Database engine and session management with Singleton pattern.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session
from config import DatabaseConfig


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
            self._engine = create_async_engine(
                DatabaseConfig.get_database_url(),
                echo=True,  # Set to False in production
                future=True,
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


# Singleton instance
db_manager = DatabaseManager()

# Expose commonly used attributes for backward compatibility
engine = db_manager.engine
AsyncSessionLocal = db_manager.session_factory


async def get_db():
    """Dependency for FastAPI to get database session."""
    async with db_manager.session_factory() as session:
        yield session
