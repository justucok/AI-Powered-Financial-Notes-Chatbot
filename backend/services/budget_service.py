from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.repositories import budget_repository, transaction_repository
    from backend.schemas.budget import (
        BudgetCreate,
        BudgetResponse,
        BudgetSummaryResponse,
        CategoryBudgetCreate,
        CategoryBudgetResponse,
        CategoryBudgetSummary,
    )
except ModuleNotFoundError:
    from repositories import budget_repository, transaction_repository
    from schemas.budget import (
        BudgetCreate,
        BudgetResponse,
        BudgetSummaryResponse,
        CategoryBudgetCreate,
        CategoryBudgetResponse,
        CategoryBudgetSummary,
    )


async def get_summary(db: AsyncSession, user_id: int, month: str) -> BudgetSummaryResponse:
    """Calculate the real-time budget vs actual expenses for the month."""
    # 1. Fetch the budget constraints
    budget_entity = await budget_repository.get_budget(db, user_id, month)
    total_budget = budget_entity.amount if budget_entity else 0.0
    category_budgets = budget_entity.category_budgets if budget_entity else []

    # 2. Fetch actual transactions for the month
    transactions = await transaction_repository.get_all(db, user_id, month)
    
    # 3. Calculate actuals
    # Only "expense" type matters for budget tracking
    expense_transactions = [t for t in transactions if t.type == "expense"]
    
    total_actual = sum(t.amount for t in expense_transactions)
    
    # Actuals by category
    category_actuals = {}
    for t in expense_transactions:
        category_actuals[t.category] = category_actuals.get(t.category, 0.0) + t.amount

    # 4. Map category budget summaries
    category_summaries = []
    for cb in category_budgets:
        actual_amt = category_actuals.get(cb.category_name, 0.0)
        remaining_amt = cb.amount - actual_amt
        percent = (actual_amt / cb.amount * 100) if cb.amount > 0 else (100.0 if actual_amt > 0 else 0.0)
        
        category_summaries.append(
            CategoryBudgetSummary(
                category_name=cb.category_name,
                budget_amount=cb.amount,
                actual_amount=actual_amt,
                remaining_amount=remaining_amt,
                percent=round(percent, 1)
            )
        )

    # 5. Overall summary
    total_remaining = total_budget - total_actual
    total_percent = (total_actual / total_budget * 100) if total_budget > 0 else (100.0 if total_actual > 0 else 0.0)

    return BudgetSummaryResponse(
        month=month,
        total_budget=total_budget,
        total_actual=total_actual,
        total_remaining=total_remaining,
        total_percent=round(total_percent, 1),
        category_budgets=category_summaries
    )


async def set_budget(db: AsyncSession, user_id: int, data: BudgetCreate) -> BudgetResponse:
    """Set or update the overall monthly budget."""
    budget = await budget_repository.upsert_budget(db, user_id, data)
    return BudgetResponse.model_validate(budget)


async def set_category_budget(db: AsyncSession, user_id: int, data: CategoryBudgetCreate) -> CategoryBudgetResponse:
    """Set or update a specific category budget for a month."""
    cb = await budget_repository.upsert_category_budget(db, user_id, data)
    return CategoryBudgetResponse.model_validate(cb)
