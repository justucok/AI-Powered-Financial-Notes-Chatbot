from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageRequest(BaseModel):
    """Request payload for text-based chat interactions."""

    message: str = Field(min_length=1)
    history: list[dict[str, Any]] = Field(default_factory=list)
    fund_sources: list[dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
