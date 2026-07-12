import logging
import os
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

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ensure the data directory exists
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Single declarative base — semua model dalam 1 DB
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Single base for all ORM models (auth + financial data)."""


_settings = get_settings()

_engine_kwargs: dict = {
    "future": True,
    "pool_pre_ping": True,
}

if not _settings.database_url.startswith("sqlite"):
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10

engine = create_async_engine(_settings.database_url, **_engine_kwargs)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db() -> None:
    """Create all tables on startup."""
    try:
        from backend.models import user, transaction, fund_source, category, budget  # noqa: F401
    except ModuleNotFoundError:
        from models import user, transaction, fund_source, category, budget  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialised: %s", _settings.database_url.split("@")[-1])


async def close_db() -> None:
    """Dispose the engine on shutdown."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for use in FastAPI Depends."""
    async with AsyncSessionFactory() as session:
        yield session
