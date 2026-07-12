from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.database import get_auth_db
    from backend.dependencies.auth import get_current_user
    from backend.schemas.auth import (
        ChangePasswordRequest,
        DeleteAccountRequest,
        LoginRequest,
        ProfileResponse,
        RegisterRequest,
        UpdateProfileRequest,
        ForgotPasswordRequest,
        ResetPasswordRequest,
        TokenPayload,
        TokenResponse,
    )
    from backend.services import auth_service
except ModuleNotFoundError:
    from database import get_auth_db
    from dependencies.auth import get_current_user
    from schemas.auth import (
        ChangePasswordRequest,
        DeleteAccountRequest,
        LoginRequest,
        ProfileResponse,
        RegisterRequest,
        UpdateProfileRequest,
        ForgotPasswordRequest,
        ResetPasswordRequest,
        TokenPayload,
        TokenResponse,
    )
    from services import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
    summary="Daftar akun baru",
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_auth_db),
) -> dict:
    """Handle new user registration with email, username, full name, and nickname."""

    try:
        return await auth_service.register_user(db, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login via email dan dapatkan JWT token",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_auth_db),
) -> TokenResponse:
    """Authenticate a user using email and password, returning a JWT access token."""

    try:
        return await auth_service.login_user(db, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post(
    "/login/form",
    response_model=TokenResponse,
    include_in_schema=False,
)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_auth_db),
) -> TokenResponse:
    """OAuth2 password-grant form login (accepts email in 'username' field for Swagger compatibility)."""

    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    try:
        return await auth_service.login_user(db, login_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get user profile",
)
async def get_profile(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_auth_db),
) -> ProfileResponse:
    """Get the profile of the currently authenticated user."""
    try:
        return await auth_service.get_profile(db, int(current_user.sub))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put(
    "/profile",
    response_model=dict,
    summary="Update user profile",
)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_auth_db),
) -> dict:
    """Update the user's profile (name and nickname)."""
    try:
        return await auth_service.update_profile(db, int(current_user.sub), data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put(
    "/password",
    response_model=dict,
    summary="Change user password",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_auth_db),
) -> dict:
    """Change the user's password."""
    try:
        return await auth_service.change_password(db, int(current_user.sub), data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete(
    "/account",
    response_model=dict,
    summary="Delete user account",
)
async def delete_account(
    data: DeleteAccountRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_auth_db),
) -> dict:
    """Delete the user account and associated personal database."""
    try:
        return await auth_service.delete_account(db, int(current_user.sub), data.password, current_user.db_path)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

@router.post(
    "/forgot-password",
    response_model=dict,
    summary="Permintaan lupa password (demo)",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_auth_db),
) -> dict:
    """Send reset password email with single-use token."""
    try:
        return await auth_service.forgot_password(db, data.email)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.post(
    "/reset-password",
    response_model=dict,
    summary="Atur ulang password (demo)",
)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_auth_db),
) -> dict:
    """Reset password immediately using single-use token."""
    try:
        return await auth_service.reset_password(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
