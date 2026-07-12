from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.repositories import fund_source_repository
    from backend.schemas.fund_source import FundSourceCreate, FundSourceResponse
except ModuleNotFoundError:
    from repositories import fund_source_repository
    from schemas.fund_source import FundSourceCreate, FundSourceResponse


async def get_fund_sources(db: AsyncSession) -> list[FundSourceResponse]:
    """Retrieve all fund sources for the current user."""
    fund_sources_data = await fund_source_repository.get_all_with_balance(db)
    return [FundSourceResponse.model_validate(fs) for fs in fund_sources_data]


async def create_fund_source(db: AsyncSession, data: FundSourceCreate) -> FundSourceResponse:
    """Create a new fund source and return it."""
    fund_source = await fund_source_repository.create(db, data)
    
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


async def delete_fund_source(db: AsyncSession, source_id: int) -> dict[str, str]:
    """Delete a fund source by ID."""
    deleted = await fund_source_repository.delete(db, source_id)
    if not deleted:
        raise ValueError(f"Sumber uang dengan ID {source_id} tidak ditemukan.")
    
    return {"message": "Sumber uang berhasil dihapus."}
