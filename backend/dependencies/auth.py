from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

try:
    from backend.schemas.auth import TokenPayload
    from backend.services import auth_service
except ModuleNotFoundError:
    from schemas.auth import TokenPayload
    from services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/form")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token autentikasi tidak valid atau sudah kadaluarsa.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return auth_service.decode_access_token(token)
    except JWTError as exc:
        raise credentials_exception from exc
