from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.repositories import transaction_repository
    from backend.schemas.transaction import (
        SummaryResponse,
        TransactionCreate,
        TransactionResponse,
    )
except ModuleNotFoundError:
    from repositories import transaction_repository
    from schemas.transaction import SummaryResponse, TransactionCreate, TransactionResponse


def _validate_month(month: str) -> str:
    """Validate and normalize a YYYY-MM month string."""

    try:
        parsed_month = datetime.strptime(month, "%Y-%m")
    except ValueError as exc:
        raise ValueError("Month must use YYYY-MM format.") from exc

    return parsed_month.strftime("%Y-%m")


def _get_current_month() -> str:
    """Return the current month in YYYY-MM format."""

    return datetime.now().strftime("%Y-%m")


async def get_transactions(
    db: AsyncSession,
    month: str | None,
) -> list[TransactionResponse]:
    """Fetch transactions and map them into response schemas."""

    normalized_month = _validate_month(month) if month is not None else None
    transactions = await transaction_repository.get_all(db, normalized_month)
    return [TransactionResponse.model_validate(transaction) for transaction in transactions]


async def create_transaction(
    db: AsyncSession,
    data: TransactionCreate,
) -> TransactionResponse:
    """Create a transaction and return the serialized result."""

    transaction = await transaction_repository.create(db, data)
    return TransactionResponse.model_validate(transaction)


async def update_transaction(
    db: AsyncSession,
    id: int,
    data: TransactionCreate,
) -> TransactionResponse:
    """Update a transaction and return the serialized result."""

    transaction = await transaction_repository.update(db, id, data)
    if transaction is None:
        raise ValueError("Transaction not found.")
    return TransactionResponse.model_validate(transaction)


async def delete_transaction(db: AsyncSession, id: int) -> dict[str, str | int]:
    """Delete a transaction and return a simple status payload."""

    transaction = await transaction_repository.delete(db, id)
    if transaction is None:
        raise ValueError("Transaction not found.")

    return {
        "message": "Transaction deleted successfully.",
        "id": id,
    }


async def get_summary(db: AsyncSession, month: str | None) -> SummaryResponse:
    """Return the monthly financial summary."""

    normalized_month = _validate_month(month) if month is not None else _get_current_month()
    summary = await transaction_repository.get_summary(db, normalized_month)
    return SummaryResponse.model_validate(summary)
