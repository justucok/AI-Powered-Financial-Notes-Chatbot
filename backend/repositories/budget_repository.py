from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.models.budget import Budget, CategoryBudget
    from backend.schemas.budget import BudgetCreate, CategoryBudgetCreate
except ModuleNotFoundError:
    from models.budget import Budget, CategoryBudget
    from schemas.budget import BudgetCreate, CategoryBudgetCreate


async def get_budget(db: AsyncSession, month: str) -> Budget | None:
    """Retrieve the global budget (ignores specific month parameter)."""
    statement = select(Budget).where(Budget.month == "ALL")
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def upsert_budget(db: AsyncSession, data: BudgetCreate) -> Budget:
    """Create or update the overall global budget."""
    budget = await get_budget(db, "ALL")
    
    if budget is None:
        budget = Budget(month="ALL", amount=data.amount)
        db.add(budget)
    else:
        budget.amount = data.amount

    await db.commit()
    await db.refresh(budget)
    return budget


async def upsert_category_budget(db: AsyncSession, data: CategoryBudgetCreate) -> CategoryBudget:
    """Create or update a category budget globally."""
    # Ensure the parent budget exists first
    budget = await get_budget(db, "ALL")
    if budget is None:
        budget = Budget(month="ALL", amount=0.0)
        db.add(budget)
        await db.flush()  # To get the budget ID
    
    # Check if category budget already exists
    statement = select(CategoryBudget).where(
        CategoryBudget.budget_id == budget.id,
        CategoryBudget.category_name == data.category_name
    )
    result = await db.execute(statement)
    category_budget = result.scalar_one_or_none()
    
    if category_budget is None:
        category_budget = CategoryBudget(
            budget_id=budget.id,
            category_name=data.category_name,
            amount=data.amount
        )
        db.add(category_budget)
    else:
        category_budget.amount = data.amount
        
    await db.commit()
    await db.refresh(category_budget)
    return category_budget
