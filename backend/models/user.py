from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from backend.database import AuthBase
except ModuleNotFoundError:
    from database import AuthBase


class User(AuthBase):
    """SQLAlchemy ORM model for the public auth-registry database.

    Each row represents one registered user. The ``db_path`` column
    stores the absolute filesystem path to that user's personal SQLite
    database, which contains their private financial transactions.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False, default="L")
    preferred_greeting: Mapped[str] = mapped_column(String(20), nullable=False, default="Bapak")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    db_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
