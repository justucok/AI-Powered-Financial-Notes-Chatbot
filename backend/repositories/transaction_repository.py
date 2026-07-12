from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.models.transaction import Transaction
    from backend.schemas.transaction import TransactionCreate
except ModuleNotFoundError:
    from models.transaction import Transaction
    from schemas.transaction import TransactionCreate


def _get_month_range(month: str) -> tuple[date, date]:
    """Convert a YYYY-MM string into an inclusive-exclusive date range."""

    year_text, month_text = month.split("-")
    year = int(year_text)
    month_number = int(month_text)

    start_date = date(year, month_number, 1)
    if month_number == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month_number + 1, 1)

    return start_date, end_date


async def get_all(db: AsyncSession, month: str | None) -> list[Transaction]:
    """Return all transactions, optionally filtered by month."""

    statement = select(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc())

    if month is not None:
        start_date, end_date = _get_month_range(month)
        statement = statement.where(
            Transaction.date >= start_date,
            Transaction.date < end_date,
        )

    result = await db.execute(statement)
    return list(result.scalars().all())


async def create(db: AsyncSession, data: TransactionCreate) -> Transaction:
    """Persist a new transaction and return the saved entity."""

    transaction = Transaction(
        type=data.type,
        amount=data.amount,
        category=data.category,
        description=data.description,
        date=data.date,
        fund_source_id=data.fund_source_id,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def update(db: AsyncSession, id: int, data: TransactionCreate) -> Transaction | None:
    """Update an existing transaction and return the updated entity when found."""

    transaction = await db.get(Transaction, id)
    if transaction is None:
        return None

    transaction.type = data.type
    transaction.amount = data.amount
    transaction.category = data.category
    transaction.description = data.description
    transaction.date = data.date
    transaction.fund_source_id = data.fund_source_id

    await db.commit()
    await db.refresh(transaction)
    return transaction


async def delete(db: AsyncSession, id: int) -> Transaction | None:
    """Delete a transaction by id and return the removed entity when found."""

    transaction = await db.get(Transaction, id)
    if transaction is None:
        return None

    await db.delete(transaction)
    await db.commit()
    return transaction


async def get_summary(db: AsyncSession, month: str) -> dict[str, float]:
    """Return the monthly income, expense, and balance summary."""

    start_date, end_date = _get_month_range(month)
    statement = select(
        func.coalesce(
            func.sum(case((Transaction.type == "income", Transaction.amount), else_=0.0)),
            0.0,
        ).label("total_income"),
        func.coalesce(
            func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0.0)),
            0.0,
        ).label("total_expense"),
    ).where(
        Transaction.date >= start_date,
        Transaction.date < end_date,
    )

    result = await db.execute(statement)
    totals = result.one()
    total_income = float(totals.total_income or 0.0)
    total_expense = float(totals.total_expense or 0.0)

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
    }
