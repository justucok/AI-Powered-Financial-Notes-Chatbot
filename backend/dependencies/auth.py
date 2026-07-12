from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.database import get_user_db
    from backend.schemas.auth import TokenPayload
    from backend.services import auth_service
except ModuleNotFoundError:
    from database import get_user_db
    from schemas.auth import TokenPayload
    from services import auth_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/form")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> TokenPayload:
    """Decode the JWT bearer token and return the current user's payload.

    This dependency is injected into every protected endpoint. It raises
    HTTP 401 if the token is missing, expired, or otherwise invalid.

    Args:
        token: The raw JWT string extracted from the ``Authorization`` header.

    Returns:
        A ``TokenPayload`` with ``sub``, ``username``, and ``db_path``.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token autentikasi tidak valid atau sudah kadaluarsa.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return auth_service.decode_access_token(token)
    except JWTError as exc:
        raise credentials_exception from exc


async def get_db_for_current_user(
    current_user: TokenPayload = Depends(get_current_user),
) -> AsyncGenerator[AsyncSession, None]:
    """Open a database session for the currently authenticated user's personal DB.

    This dependency resolves ``db_path`` from the JWT token and yields an
    async session bound to that user's isolated SQLite database.

    Args:
        current_user: The decoded token payload (injected by ``get_current_user``).

    Yields:
        An ``AsyncSession`` bound to the user's personal financial database.
    """

    async for session in get_user_db(current_user.db_path):
        yield session
