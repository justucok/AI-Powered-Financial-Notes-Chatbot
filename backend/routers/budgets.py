import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.dependencies.auth import get_db_for_current_user
    from backend.schemas.budget import (
        BudgetCreate,
        BudgetResponse,
        BudgetSummaryResponse,
        CategoryBudgetCreate,
        CategoryBudgetResponse,
    )
    from backend.services import budget_service
except ModuleNotFoundError:
    from dependencies.auth import get_db_for_current_user
    from schemas.budget import (
        BudgetCreate,
        BudgetResponse,
        BudgetSummaryResponse,
        CategoryBudgetCreate,
        CategoryBudgetResponse,
    )
    from services import budget_service


router = APIRouter(tags=["budgets"])


@router.get("/budgets/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    month: Annotated[str, Query(description="Month to retrieve budget summary for (YYYY-MM)")],
    db: AsyncSession = Depends(get_db_for_current_user),
) -> BudgetSummaryResponse:
    """Retrieve the budget summary (budget vs actual expenses) for a specific month."""
    
    if not re.match(r"^\d{4}-\d{2}$", month):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Month must be in YYYY-MM format",
        )

    return await budget_service.get_summary(db, month)


@router.post(
    "/budgets",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def set_budget(
    data: BudgetCreate,
    db: AsyncSession = Depends(get_db_for_current_user),
) -> BudgetResponse:
    """Set or update the overall budget limit for a specific month."""
    
    return await budget_service.set_budget(db, data)


@router.post(
    "/budgets/categories",
    response_model=CategoryBudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def set_category_budget(
    data: CategoryBudgetCreate,
    db: AsyncSession = Depends(get_db_for_current_user),
) -> CategoryBudgetResponse:
    """Set or update the budget limit for a specific category within a month."""
    
    return await budget_service.set_category_budget(db, data)
