from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

try:
    from backend.models.fund_source import FundSource
    from backend.models.transaction import Transaction
    from backend.schemas.fund_source import FundSourceCreate
except ModuleNotFoundError:
    from models.fund_source import FundSource
    from models.transaction import Transaction
    from schemas.fund_source import FundSourceCreate


async def get_real_time_balance(db: AsyncSession, user_id: int, id: int) -> float | None:
    """Return the real-time balance of a single fund source, or None if not found."""
    fs = await get_by_id(db, user_id, id)
    if not fs:
        return None

    tx_sum_stmt = select(
        func.coalesce(func.sum(case((Transaction.type == "income", Transaction.amount), else_=0.0)), 0.0),
        func.coalesce(func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0.0)), 0.0),
    ).where(Transaction.fund_source_id == id, Transaction.user_id == user_id)

    result = await db.execute(tx_sum_stmt)
    total_income, total_expense = result.first()
    
    return fs.initial_balance + float(total_income or 0.0) - float(total_expense or 0.0)


async def get_all_with_balance(db: AsyncSession, user_id: int) -> list[dict]:
    """Return all fund sources with computed real-time balance.
    balance = initial_balance + SUM(income) - SUM(expense)
    """

    # Subquery to calculate sum of transactions per fund_source
    tx_sum_stmt = (
        select(
            Transaction.fund_source_id,
            func.coalesce(
                func.sum(case((Transaction.type == "income", Transaction.amount), else_=0.0)),
                0.0,
            ).label("total_income"),
            func.coalesce(
                func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0.0)),
                0.0,
            ).label("total_expense"),
        )
        .where(Transaction.fund_source_id.is_not(None), Transaction.user_id == user_id)
        .group_by(Transaction.fund_source_id)
        .subquery()
    )

    # Join fund_sources with the transaction sums
    stmt = select(
        FundSource,
        tx_sum_stmt.c.total_income,
        tx_sum_stmt.c.total_expense,
    ).outerjoin(tx_sum_stmt, FundSource.id == tx_sum_stmt.c.fund_source_id).where(
        FundSource.user_id == user_id
    )

    result = await db.execute(stmt)
    rows = result.all()

    fund_sources = []
    for fs, total_income, total_expense in rows:
        inc = float(total_income or 0.0)
        exp = float(total_expense or 0.0)
        current_balance = fs.initial_balance + inc - exp

        fs_dict = {
            "id": fs.id,
            "name": fs.name,
            "type": fs.type,
            "icon": fs.icon,
            "initial_balance": fs.initial_balance,
            "balance": current_balance,
            "created_at": fs.created_at,
        }
        fund_sources.append(fs_dict)

    return fund_sources


async def create(db: AsyncSession, user_id: int, data: FundSourceCreate) -> FundSource:
    """Persist a new fund source and return the saved entity."""
    fund_source = FundSource(
        user_id=user_id,
        name=data.name,
        type=data.type,
        icon=data.icon,
        initial_balance=data.initial_balance,
    )
    db.add(fund_source)
    await db.commit()
    await db.refresh(fund_source)
    return fund_source


async def delete(db: AsyncSession, user_id: int, id: int) -> FundSource | None:
    """Delete a fund source by id and return the removed entity when found."""
    statement = select(FundSource).where(FundSource.id == id, FundSource.user_id == user_id)
    fund_source = await db.scalar(statement)
    if fund_source is None:
        return None

    await db.delete(fund_source)
    await db.commit()
    return fund_source


async def get_by_id(db: AsyncSession, user_id: int, id: int) -> FundSource | None:
    """Get a fund source by id."""
    statement = select(FundSource).where(FundSource.id == id, FundSource.user_id == user_id)
    return await db.scalar(statement)
