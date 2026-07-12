from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.models.user import User
except ModuleNotFoundError:
    from models.user import User


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    """Return the user with the given email, or None if not found."""

    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    email: str,
    full_name: str,
    nickname: str,
    hashed_password: str,
) -> User:
    """Create a new user account in the database."""

    user = User(
        email=email,
        full_name=full_name,
        nickname=nickname,
        hashed_password=hashed_password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Return the user with the given id, or None if not found."""
    return await db.get(User, user_id)


async def delete_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Delete a user by id and return the removed entity when found."""
    user = await get_by_id(db, user_id)
    if user is None:
        return None

    await db.delete(user)
    await db.commit()
    return user
