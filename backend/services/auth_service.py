import logging
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.config import get_settings
    from backend.database import DATA_DIR, init_user_db
    from backend.repositories import user_repository
    from backend.schemas.auth import LoginRequest, RegisterRequest, TokenPayload, TokenResponse
except ModuleNotFoundError:
    from config import get_settings
    from database import DATA_DIR, init_user_db
    from repositories import user_repository
    from schemas.auth import LoginRequest, RegisterRequest, TokenPayload, TokenResponse

logger = logging.getLogger(__name__)

_settings = get_settings()

ALGORITHM = "HS256"
_BCRYPT_ROUNDS = 12


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Return the bcrypt hash of a plaintext password."""

    password_bytes = plain.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=_BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""

    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------


def create_access_token(payload: dict[str, Any]) -> str:
    """Create a signed JWT access token with an expiry claim."""

    expire = datetime.now(UTC) + timedelta(days=_settings.access_token_expire_days)
    to_encode = {**payload, "exp": expire}
    return jwt.encode(to_encode, _settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JWT access token."""

    claims = jwt.decode(token, _settings.secret_key, algorithms=[ALGORITHM])
    return TokenPayload(
        sub=str(claims["sub"]),
        email=str(claims["email"]),
        full_name=str(claims["full_name"]),
        nickname=str(claims["nickname"]),
        preferred_greeting=str(claims.get("preferred_greeting", "")),
        db_path=str(claims["db_path"]),
    )


# ---------------------------------------------------------------------------
# Business logic — register & login
# ---------------------------------------------------------------------------


async def register_user(db: AsyncSession, data: RegisterRequest) -> dict[str, str]:
    """Register a new user account and provision their personal database."""

    # 1. Cek email unik
    existing_email = await user_repository.get_by_email(db, data.email)
    if existing_email is not None:
        raise ValueError(f"Email '{data.email}' sudah terdaftar.")

    hashed = hash_password(data.password)
    db_filename = f"db_{uuid.uuid4().hex}.sqlite3"
    db_path = os.path.join(DATA_DIR, db_filename)

    # Default greeting based on gender
    greeting = "Bapak" if data.gender.upper() == "L" else "Ibu"

    user = await user_repository.create(
        db=db,
        email=data.email,
        full_name=data.full_name,
        nickname=data.nickname,
        hashed_password=hashed,
        db_path=db_path,
    )
    user.gender = data.gender
    user.preferred_greeting = greeting
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("Registered new user (%s) with db_path='%s'", user.email, db_path)

    # Provision the per-user database
    await init_user_db(db_path)
    logger.info("Initialised user database at '%s'", db_path)
    
    # Add initial FundSource
    try:
        from backend.database import get_user_db
        from backend.models.fund_source import FundSource
    except ModuleNotFoundError:
        from database import get_user_db
        from models.fund_source import FundSource
    
    user_db_gen = get_user_db(db_path)
    user_db_session = await anext(user_db_gen)
    try:
        user_db_session.add(FundSource(name="Cash", type="cash", icon="💵"))
        await user_db_session.commit()
    finally:
        try:
            await anext(user_db_gen)
        except StopAsyncIteration:
            pass

    return {"message": "Pendaftaran berhasil."}


async def login_user(db: AsyncSession, data: LoginRequest) -> TokenResponse:
    """Authenticate a user using email and return a signed JWT access token."""

    user = await user_repository.get_by_email(db, data.email)
    if user is None or not verify_password(data.password, user.hashed_password):
        raise ValueError("Email atau password tidak valid.")

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "nickname": user.nickname,
        "preferred_greeting": user.preferred_greeting,
        "db_path": user.db_path,
    }
    token = create_access_token(token_payload)
    logger.info("User email '%s' logged in successfully.", user.email)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        full_name=user.full_name,
        nickname=user.nickname,
        preferred_greeting=user.preferred_greeting,
    )


async def get_profile(db: AsyncSession, user_id: int):
    """Retrieve user profile."""
    user = await user_repository.get_by_id(db, user_id)
    if not user:
        raise ValueError("Pengguna tidak ditemukan.")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "nickname": user.nickname,
        "preferred_greeting": user.preferred_greeting,
        "created_at": user.created_at.isoformat(),
    }


async def change_password(db: AsyncSession, user_id: int, data) -> dict:
    """Change the user's password."""
    user = await user_repository.get_by_id(db, user_id)
    if not user or not verify_password(data.current_password, user.hashed_password):
        raise ValueError("Password saat ini tidak valid.")
    
    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    await db.commit()
    return {"message": "Password berhasil diubah."}


async def update_profile(db: AsyncSession, user_id: int, data) -> dict:
    """Update user profile (full name, nickname)."""
    user = await user_repository.get_by_id(db, user_id)
    if not user:
        raise ValueError("Pengguna tidak ditemukan.")
    
    user.full_name = data.full_name
    user.nickname = data.nickname
    if data.preferred_greeting:
        user.preferred_greeting = data.preferred_greeting
    db.add(user)
    await db.commit()
    
    return {
        "message": "Profil berhasil diperbarui.",
        "full_name": user.full_name,
        "nickname": user.nickname,
        "preferred_greeting": user.preferred_greeting,
    }


async def delete_account(db: AsyncSession, user_id: int, password: str, db_path: str) -> dict:
    """Delete the user account and their personal database."""
    user = await user_repository.get_by_id(db, user_id)
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Password tidak valid. Penghapusan akun dibatalkan.")
    
    # 1. Delete from auth DB
    await user_repository.delete_by_id(db, user_id)
    
    # 2. Delete the physical SQLite file for the user
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Deleted physical database for user %s at %s", user_id, db_path)
    except Exception as e:
        logger.warning("Failed to delete physical database %s: %s", db_path, e)

    return {"message": "Akun berhasil dihapus permanen."}

def create_reset_token(user) -> str:
    """Membuat JWT token reset berdurasi 15 menit, menggunakan secret = secret_key + user.hashed_password."""
    from datetime import UTC, datetime, timedelta
    from jose import jwt
    expire = datetime.now(UTC) + timedelta(minutes=15)
    payload = {"sub": str(user.id), "email": user.email, "exp": expire}
    # Secret dinamis berdasarkan password hash saat ini
    secret = _settings.secret_key + user.hashed_password
    return jwt.encode(payload, secret, algorithm=ALGORITHM)

async def forgot_password(db: AsyncSession, email: str) -> dict:
    """Mencari user, generate token, dan memanggil email_service."""
    user = await user_repository.get_by_email(db, email)
    if not user:
        raise ValueError("Email belum terdaftar di sistem kami.")
        
    token = create_reset_token(user)
    reset_link = f"{_settings.frontend_url}/?reset_token={token}"
    
    try:
        from backend.services.email_service import send_reset_email
    except ModuleNotFoundError:
        from services.email_service import send_reset_email
        
    send_reset_email(user.email, reset_link)
    return {"message": "Tautan atur ulang password telah dikirim ke email Anda."}

async def reset_password(db: AsyncSession, data) -> dict:
    """Verifikasi token JWT dinamis dan ubah password."""
    from jose import jwt, JWTError
    
    # 1. Decode payload tanpa verifikasi dulu untuk mencari sub (user_id)
    try:
        unverified_claims = jwt.get_unverified_claims(data.token)
        user_id = int(unverified_claims["sub"])
    except Exception:
        raise ValueError("Tautan tidak valid atau rusak.")
        
    # 2. Ambil user dari DB
    user = await user_repository.get_by_id(db, user_id)
    if not user:
        raise ValueError("Pengguna tidak ditemukan.")
        
    # 3. Verifikasi token menggunakan secret dinamis (secret_key + hashed_password)
    secret = _settings.secret_key + user.hashed_password
    try:
        jwt.decode(data.token, secret, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Tautan tidak valid, sudah kadaluwarsa, atau sudah pernah digunakan.")
        
    # 4. Update password
    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    await db.commit()
    return {"message": "Password berhasil diatur ulang."}
