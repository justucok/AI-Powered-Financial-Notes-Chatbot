from datetime import datetime
from sqlalchemy import Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from backend.database import UserDataBase
except ModuleNotFoundError:
    from database import UserDataBase


class Budget(UserDataBase):
    """SQLAlchemy ORM model for overall monthly budget (per-user database)."""
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, unique=True)  # Format: YYYY-MM
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )

    category_budgets: Mapped[list["CategoryBudget"]] = relationship(
        "CategoryBudget",
        back_populates="budget",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class CategoryBudget(UserDataBase):
    """SQLAlchemy ORM model for category budgets (per-user database)."""
    __tablename__ = "category_budgets"
    __table_args__ = (
        UniqueConstraint("budget_id", "category_name", name="uq_budget_category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )

    budget: Mapped["Budget"] = relationship("Budget", back_populates="category_budgets")
