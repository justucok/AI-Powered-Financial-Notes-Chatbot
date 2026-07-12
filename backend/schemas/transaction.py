from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TransactionType = Literal["income", "expense"]


class TransactionCreate(BaseModel):
    """Request payload for creating a transaction."""

    type: TransactionType
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    date: date
    fund_source_id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    """Response payload for a transaction record."""

    id: int
    type: TransactionType
    amount: float
    category: str
    description: str | None
    date: date
    fund_source_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SummaryResponse(BaseModel):
    """Response payload for aggregated financial summary."""

    total_income: float = 0
    total_expense: float = 0
    balance: float = 0

    model_config = ConfigDict(from_attributes=True)
