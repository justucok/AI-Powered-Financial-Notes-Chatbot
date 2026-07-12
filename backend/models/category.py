from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from backend.database import UserDataBase
except ModuleNotFoundError:
    from database import UserDataBase


class Category(UserDataBase):
    """SQLAlchemy ORM model for categories (per-user database)."""

    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense')",
            name="ck_categories_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
