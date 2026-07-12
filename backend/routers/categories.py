from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.dependencies.auth import get_db_for_current_user
    from backend.schemas.category import CategoryCreate, CategoryResponse
    from backend.services import category_service
except ModuleNotFoundError:
    from dependencies.auth import get_db_for_current_user
    from schemas.category import CategoryCreate, CategoryResponse
    from services import category_service


router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db_for_current_user)):
    """Retrieve all categories for the current user."""
    return await category_service.get_categories(db)


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db_for_current_user)
):
    """Create a new custom category."""
    return await category_service.create_category(db, data)


@router.delete("/categories/{id}")
async def delete_category(id: int, db: AsyncSession = Depends(get_db_for_current_user)):
    """Delete a category by its ID."""
    try:
        return await category_service.delete_category(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
