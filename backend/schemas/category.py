from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Payload for creating a new custom category."""

    name: str = Field(min_length=1, max_length=100)
    type: str = Field(pattern="^(income|expense)$")
    icon: str | None = Field(default=None, max_length=20)


class CategoryResponse(BaseModel):
    """Response payload for a category."""

    id: int
    name: str
    type: str
    icon: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
