from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

try:
    from backend.config import get_settings
except ModuleNotFoundError:
    from config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


engine = create_async_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
)
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create database tables during application startup."""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose the database engine during application shutdown."""

    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for FastAPI dependencies."""

    async with AsyncSessionFactory() as session:
        yield session
