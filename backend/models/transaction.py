from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base


class Transaction(Base):
    """SQLAlchemy ORM model for financial transactions."""

    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense')",
            name="ck_transactions_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
