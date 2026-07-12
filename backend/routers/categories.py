from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.database import get_db
    from backend.dependencies.auth import get_current_user
    from backend.schemas.auth import TokenPayload
    from backend.schemas.category import CategoryCreate, CategoryResponse
    from backend.services import category_service
except ModuleNotFoundError:
    from database import get_db
    from dependencies.auth import get_current_user
    from schemas.auth import TokenPayload
    from schemas.category import CategoryCreate, CategoryResponse
    from services import category_service


router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Retrieve all categories for the current user."""
    return await category_service.get_categories(db, int(current_user.sub))


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Create a new custom category."""
    return await category_service.create_category(db, int(current_user.sub), data)


@router.delete("/categories/{id}")
async def delete_category(
    id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Delete a category by its ID."""
    try:
        return await category_service.delete_category(db, int(current_user.sub), id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
