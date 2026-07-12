from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.dependencies.auth import get_db_for_current_user
    from backend.schemas.transaction import (
        SummaryResponse,
        TransactionCreate,
        TransactionResponse,
    )
    from backend.services import transaction_service
except ModuleNotFoundError:
    from dependencies.auth import get_db_for_current_user
    from schemas.transaction import SummaryResponse, TransactionCreate, TransactionResponse
    from services import transaction_service


router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    month: Annotated[str | None, Query(description="Filter transactions by YYYY-MM")] = None,
    db: AsyncSession = Depends(get_db_for_current_user),
) -> list[TransactionResponse]:
    """Handle requests for listing transactions (authenticated user only)."""

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
    db: AsyncSession = Depends(get_db_for_current_user),
) -> TransactionResponse:
    """Handle requests for creating a transaction (authenticated user only)."""

    return await transaction_service.create_transaction(db, data)


from pydantic import BaseModel
class ConfirmTransactionsRequest(BaseModel):
    transactions: list[TransactionCreate]


@router.post(
    "/transactions/confirm",
    response_model=list[TransactionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def confirm_transactions(
    data: ConfirmTransactionsRequest,
    db: AsyncSession = Depends(get_db_for_current_user),
) -> list[TransactionResponse]:
    """Save multiple pending transactions after fund source selection."""
    # Create each transaction one by one
    responses = []
    for tx_data in data.transactions:
        responses.append(await transaction_service.create_transaction(db, tx_data))
    return responses


@router.put("/transactions/{id}", response_model=TransactionResponse)
async def update_transaction(
    id: int,
    data: TransactionCreate,
    db: AsyncSession = Depends(get_db_for_current_user),
) -> TransactionResponse:
    """Handle requests for updating a transaction (authenticated user only)."""

    try:
        return await transaction_service.update_transaction(db, id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete("/transactions/{id}", response_model=dict[str, str | int])
async def delete_transaction(
    id: int,
    db: AsyncSession = Depends(get_db_for_current_user),
) -> dict[str, str | int]:
    """Handle requests for deleting a transaction (authenticated user only)."""

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
    db: AsyncSession = Depends(get_db_for_current_user),
) -> SummaryResponse:
    """Handle requests for fetching the monthly summary (authenticated user only)."""

    try:
        return await transaction_service.get_summary(db, month)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
