from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.database import get_db
    from backend.schemas.transaction import (
        SummaryResponse,
        TransactionCreate,
        TransactionResponse,
    )
    from backend.services import transaction_service
except ModuleNotFoundError:
    from database import get_db
    from schemas.transaction import SummaryResponse, TransactionCreate, TransactionResponse
    from services import transaction_service


router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    month: Annotated[str | None, Query(description="Filter transactions by YYYY-MM")] = None,
    db: AsyncSession = Depends(get_db),
) -> list[TransactionResponse]:
    """Handle requests for listing transactions."""

    try:
        return await transaction_service.get_transactions(db, month)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """Handle requests for creating a transaction."""

    return await transaction_service.create_transaction(db, data)


@router.delete("/transactions/{id}", response_model=dict[str, str | int])
async def delete_transaction(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str | int]:
    """Handle requests for deleting a transaction."""

    try:
        return await transaction_service.delete_transaction(db, id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    month: Annotated[str | None, Query(description="Filter summary by YYYY-MM")] = None,
    db: AsyncSession = Depends(get_db),
) -> SummaryResponse:
    """Handle requests for fetching the monthly summary."""

    try:
        return await transaction_service.get_summary(db, month)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
