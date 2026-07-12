from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FundSourceCreate(BaseModel):
    """Payload for creating a new fund source."""

    name: str = Field(min_length=1, max_length=100)
    type: str = Field(pattern="^(bank|ewallet|cash|other)$")
    icon: str | None = None
    initial_balance: float = Field(default=0.0, ge=0)


class FundSourceResponse(BaseModel):
    """Response payload for a fund source, including its computed real-time balance."""

    id: int
    name: str
    type: str
    icon: str | None
    initial_balance: float
    balance: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdjustBalanceRequest(BaseModel):
    """Payload for adjusting fund source balance to a target value."""
    
    target_balance: float = Field(ge=0, description="Saldo yang diinginkan setelah penyesuaian")
