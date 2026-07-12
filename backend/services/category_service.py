from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.repositories import category_repository
    from backend.schemas.category import CategoryCreate, CategoryResponse
except ModuleNotFoundError:
    from repositories import category_repository
    from schemas.category import CategoryCreate, CategoryResponse


DEFAULT_CATEGORIES = [
    ("Makanan", "expense", "🍔"),
    ("Transport", "expense", "🚗"),
    ("Belanja", "expense", "🛍️"),
    ("Kesehatan", "expense", "🏥"),
    ("Hiburan", "expense", "🎬"),
    ("Tagihan", "expense", "🔌"),
    ("Pendidikan", "expense", "📚"),
    ("Lainnya", "expense", "🌐"),
    ("Gaji", "income", "💰"),
    ("Freelance", "income", "💻"),
    ("Investasi", "income", "📈"),
    ("Bonus", "income", "🎁"),
    ("Hadiah", "income", "🧧"),
    ("Penjualan", "income", "🛍️"),
    ("Lainnya", "income", "🌐"),
]


async def get_categories(db: AsyncSession) -> list[CategoryResponse]:
    """Retrieve all categories. Seeds default categories if none exist."""
    categories = await category_repository.get_all(db)
    
    if not categories:
        # Lazy seeding
        for name, type_val, icon in DEFAULT_CATEGORIES:
            data = CategoryCreate(name=name, type=type_val, icon=icon)
            await category_repository.create(db, data)
        # Fetch again after seeding
        categories = await category_repository.get_all(db)

    return [CategoryResponse.model_validate(c) for c in categories]


async def create_category(db: AsyncSession, data: CategoryCreate) -> CategoryResponse:
    """Create a new custom category."""
    category = await category_repository.create(db, data)
    return CategoryResponse.model_validate(category)


async def delete_category(db: AsyncSession, id: int) -> dict[str, str]:
    """Delete a category by its ID."""
    category = await category_repository.delete(db, id)
    if not category:
        raise ValueError("Kategori tidak ditemukan.")
    
    return {"message": "Kategori berhasil dihapus."}
