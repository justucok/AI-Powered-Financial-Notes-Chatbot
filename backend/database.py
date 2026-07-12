import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# Ensure the data directory exists
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

AUTH_DB_PATH = os.path.join(DATA_DIR, "auth.db")
AUTH_DB_URL = f"sqlite+aiosqlite:///{AUTH_DB_PATH}"


# ---------------------------------------------------------------------------
# Declarative bases — auth and user-data are kept completely separate
# ---------------------------------------------------------------------------


class AuthBase(DeclarativeBase):
    """Base class for the public auth-registry ORM models."""


class UserDataBase(DeclarativeBase):
    """Base class for per-user financial-data ORM models."""


# ---------------------------------------------------------------------------
# Auth DB — single engine shared across the application lifetime
# ---------------------------------------------------------------------------

auth_engine = create_async_engine(
    AUTH_DB_URL,
    future=True,
    pool_pre_ping=True,
)
AuthAsyncSessionFactory = async_sessionmaker(
    bind=auth_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_auth_db() -> None:
    """Create auth-registry tables during application startup."""

    # Import here to avoid circular imports
    try:
        from backend.models import user  # noqa: F401
    except ModuleNotFoundError:
        from models import user  # noqa: F401

    async with auth_engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)


async def close_auth_db() -> None:
    """Dispose the auth database engine during application shutdown."""

    await auth_engine.dispose()


async def get_auth_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an auth-registry database session for FastAPI dependencies."""

    async with AuthAsyncSessionFactory() as session:
        yield session


# ---------------------------------------------------------------------------
# Per-user DB — engine created on-demand from the user's db_path
# ---------------------------------------------------------------------------


async def get_user_db(db_path: str) -> AsyncGenerator[AsyncSession, None]:
    """Yield a session for the user's personal financial database.

    A fresh engine is created per-request and disposed afterwards.
    This is acceptable for SQLite where connection overhead is minimal.
    """

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        future=True,
    )
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()


async def init_user_db(db_path: str) -> None:
    """Create transaction tables in a newly provisioned user database."""

    try:
        from backend.models.transaction import Transaction  # noqa: F401
        from backend.models.fund_source import FundSource   # noqa: F401
        from backend.models.category import Category        # noqa: F401
        from backend.models.budget import Budget, CategoryBudget  # noqa: F401
    except ModuleNotFoundError:
        from models.transaction import Transaction  # noqa: F401
        from models.fund_source import FundSource   # noqa: F401
        from models.category import Category        # noqa: F401
        from models.budget import Budget, CategoryBudget  # noqa: F401

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(UserDataBase.metadata.create_all)
    await engine.dispose()
