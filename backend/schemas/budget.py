from pydantic import BaseModel, ConfigDict, Field


class CategoryBudgetBase(BaseModel):
    category_name: str = Field(min_length=1, max_length=100)
    amount: float = Field(ge=0.0)


class CategoryBudgetResponse(CategoryBudgetBase):
    id: int
    budget_id: int
    
    model_config = ConfigDict(from_attributes=True)


class BudgetCreate(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    amount: float = Field(ge=0.0)


class CategoryBudgetCreate(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    category_name: str = Field(min_length=1, max_length=100)
    amount: float = Field(ge=0.0)


class BudgetResponse(BaseModel):
    id: int
    month: str
    amount: float
    category_budgets: list[CategoryBudgetResponse] = []

    model_config = ConfigDict(from_attributes=True)


class CategoryBudgetSummary(BaseModel):
    category_name: str
    budget_amount: float
    actual_amount: float
    remaining_amount: float
    percent: float


class BudgetSummaryResponse(BaseModel):
    month: str
    total_budget: float
    total_actual: float
    total_remaining: float
    total_percent: float
    category_budgets: list[CategoryBudgetSummary] = []
