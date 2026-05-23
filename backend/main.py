from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

try:
    from backend.config import get_settings
    from backend.database import close_db, init_db
    from backend.models import transaction  # noqa: F401
    from backend.routers.chat import router as chat_router
    from backend.routers.transactions import router as transactions_router
    from backend.services.gemini_service import close_gemini_client
except ModuleNotFoundError:
    from config import get_settings
    from database import close_db, init_db
    from models import transaction  # noqa: F401
    from routers.chat import router as chat_router
    from routers.transactions import router as transactions_router
    from services.gemini_service import close_gemini_client


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize and dispose shared resources for the application."""

    await init_db()
    try:
        yield
    finally:
        await close_gemini_client()
        await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description="Backend API for the AI-Powered Financial Notes Chatbot.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(chat_router, prefix=settings.api_v1_prefix)
    app.include_router(transactions_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
