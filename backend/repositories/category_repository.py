from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.models.category import Category
    from backend.schemas.category import CategoryCreate
except ModuleNotFoundError:
    from models.category import Category
    from schemas.category import CategoryCreate


async def get_all(db: AsyncSession) -> list[Category]:
    """Return all categories."""
    result = await db.execute(select(Category))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: CategoryCreate) -> Category:
    """Persist a new category and return the saved entity."""
    category = Category(
        name=data.name,
        type=data.type,
        icon=data.icon,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def delete(db: AsyncSession, id: int) -> Category | None:
    """Delete a category by id and return the removed entity when found."""
    category = await db.get(Category, id)
    if category is None:
        return None

    await db.delete(category)
    await db.commit()
    return category
