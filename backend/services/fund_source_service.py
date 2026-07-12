from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.repositories import fund_source_repository
    from backend.schemas.fund_source import FundSourceCreate, FundSourceResponse
except ModuleNotFoundError:
    from repositories import fund_source_repository
    from schemas.fund_source import FundSourceCreate, FundSourceResponse


async def get_fund_sources(db: AsyncSession, user_id: int) -> list[FundSourceResponse]:
    """Retrieve all fund sources for the current user."""
    fund_sources_data = await fund_source_repository.get_all_with_balance(db, user_id)
    return [FundSourceResponse.model_validate(fs) for fs in fund_sources_data]


async def create_fund_source(db: AsyncSession, user_id: int, data: FundSourceCreate) -> FundSourceResponse:
    """Create a new fund source and return it."""
    fund_source = await fund_source_repository.create(db, user_id, data)
    
    # After creation, the balance is just the initial_balance since there are no transactions yet
    fs_dict = {
        "id": fund_source.id,
        "name": fund_source.name,
        "type": fund_source.type,
        "icon": fund_source.icon,
        "initial_balance": fund_source.initial_balance,
        "balance": fund_source.initial_balance,
        "created_at": fund_source.created_at,
    }
    return FundSourceResponse.model_validate(fs_dict)


async def delete_fund_source(db: AsyncSession, user_id: int, source_id: int) -> dict[str, str]:
    """Delete a fund source by ID."""
    deleted = await fund_source_repository.delete(db, user_id, source_id)
    if not deleted:
        raise ValueError(f"Sumber uang dengan ID {source_id} tidak ditemukan.")
    return {"message": "Sumber uang berhasil dihapus."}


async def adjust_balance(
    db: AsyncSession, user_id: int, source_id: int, target_balance: float
) -> dict:
    """
    Adjust a fund source balance to match a target value.
    Computes delta against the real-time balance and creates one adjustment transaction.
    """
    from datetime import date as date_type
    
    try:
        from backend.repositories import transaction_repository
        from backend.schemas.transaction import TransactionCreate
    except ModuleNotFoundError:
        from repositories import transaction_repository
        from schemas.transaction import TransactionCreate

    fund_source = await fund_source_repository.get_by_id(db, user_id, source_id)
    if not fund_source:
        raise ValueError(f"Sumber uang dengan ID {source_id} tidak ditemukan.")

    current_balance = await fund_source_repository.get_real_time_balance(db, user_id, source_id)
    if current_balance is None:
        raise ValueError(f"Sumber uang dengan ID {source_id} tidak ditemukan.")
        
    delta = target_balance - current_balance

    if abs(delta) < 0.01:
        return {"message": "Tidak ada perubahan saldo diperlukan."}

    tx_type = "income" if delta > 0 else "expense"
    tx_amount = abs(delta)
    description = f"Penyesuaian saldo: {fund_source.name} (adjustment)"

    tx_data = TransactionCreate(
        type=tx_type,
        amount=tx_amount,
        category="Adjustment",
        description=description,
        date=date_type.today(),
        fund_source_id=source_id,
    )
    await transaction_repository.create(db, user_id, tx_data)

    return {
        "message": f"Saldo berhasil disesuaikan. Transaksi {tx_type} Rp {tx_amount:,.0f} telah dibuat.",
        "transaction_type": tx_type,
        "amount": tx_amount,
        "new_balance": target_balance,
    }
