from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.database import get_db
    from backend.dependencies.auth import get_current_user
    from backend.schemas.auth import TokenPayload
    from backend.schemas.fund_source import FundSourceCreate, FundSourceResponse
    from backend.services import fund_source_service
except ModuleNotFoundError:
    from database import get_db
    from dependencies.auth import get_current_user
    from schemas.auth import TokenPayload
    from schemas.fund_source import FundSourceCreate, FundSourceResponse
    from services import fund_source_service


router = APIRouter(prefix="/fund-sources", tags=["fund-sources"])


@router.get(
    "/",
    response_model=list[FundSourceResponse],
    summary="Get all fund sources with their balances",
)
async def get_fund_sources(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
) -> list[FundSourceResponse]:
    """Retrieve all fund sources for the current user and compute their current balance."""
    return await fund_source_service.get_fund_sources(db, int(current_user.sub))


@router.post(
    "/",
    response_model=FundSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fund source",
)
async def create_fund_source(
    data: FundSourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
) -> FundSourceResponse:
    """Create a new fund source with an initial balance."""
    return await fund_source_service.create_fund_source(db, int(current_user.sub), data)


@router.delete(
    "/{source_id}",
    response_model=dict,
    summary="Delete a fund source",
)
async def delete_fund_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    """Delete a fund source by ID."""
    try:
        return await fund_source_service.delete_fund_source(db, int(current_user.sub), source_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
