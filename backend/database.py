import logging
import os
from collections.abc import AsyncGenerator
from pathlib import Path

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
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

# ---------------------------------------------------------------------------
# Ensure the data directory exists
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(BACKEND_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def _normalize_database_url(database_url: str) -> str:
    """Return a SQLite URL that is safe regardless of the current working directory."""

    sqlite_async_prefix = "sqlite+aiosqlite:///"
    sqlite_sync_prefix = "sqlite:///"
    prefix = ""

    if database_url.startswith(sqlite_async_prefix):
        prefix = sqlite_async_prefix
    elif database_url.startswith(sqlite_sync_prefix):
        prefix = sqlite_sync_prefix
    else:
        return database_url

    db_path = database_url.removeprefix(prefix)
    if db_path == ":memory:" or os.path.isabs(db_path):
        return database_url

    relative_path = Path(db_path)
    absolute_path = PROJECT_DIR / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    return f"{prefix}{absolute_path}"


# ---------------------------------------------------------------------------
# Single declarative base — semua model dalam 1 DB
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Single base for all ORM models (auth + financial data)."""


_settings = get_settings()
_database_url = _normalize_database_url(_settings.database_url)

_engine_kwargs: dict = {
    "future": True,
    "pool_pre_ping": True,
}

if not _database_url.startswith("sqlite"):
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10

engine = create_async_engine(_database_url, **_engine_kwargs)

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
    logger.info("Database initialised: %s", _database_url.split("@")[-1])


async def close_db() -> None:
    """Dispose the engine on shutdown."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for use in FastAPI Depends."""
    async with AsyncSessionFactory() as session:
        yield session
