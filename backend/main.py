from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.config import get_settings
    from backend.database import close_auth_db, init_auth_db
    from backend.models import transaction, user  # noqa: F401 — registers ORM models
    from backend.routers.auth import router as auth_router
    from backend.routers.chat import router as chat_router
    from backend.routers.fund_sources import router as fund_sources_router
    from backend.routers.transactions import router as transactions_router
    from backend.routers.categories import router as categories_router
    from backend.routers.budgets import router as budgets_router
    from backend.services.gemini_service import close_gemini_client
except ModuleNotFoundError:
    from config import get_settings
    from database import close_auth_db, init_auth_db
    from models import transaction, user  # noqa: F401
    from routers.auth import router as auth_router
    from routers.chat import router as chat_router
    from routers.fund_sources import router as fund_sources_router
    from routers.transactions import router as transactions_router
    from routers.categories import router as categories_router
    from routers.budgets import router as budgets_router
    from services.gemini_service import close_gemini_client


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize and dispose shared resources for the application."""

    # Initialize the public auth-registry database
    await init_auth_db()
    try:
        yield
    finally:
        await close_gemini_client()
        await close_auth_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description="Backend API for the AI-Powered Financial Notes Chatbot with per-user isolated databases.",
        version="2.0.0",
        lifespan=lifespan,
    )

    # Allow frontend dev server to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(chat_router, prefix=settings.api_v1_prefix)
    app.include_router(fund_sources_router, prefix=settings.api_v1_prefix)
    app.include_router(transactions_router, prefix=settings.api_v1_prefix)
    app.include_router(categories_router, prefix=settings.api_v1_prefix)
    app.include_router(budgets_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
