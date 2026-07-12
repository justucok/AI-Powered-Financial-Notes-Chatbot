from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    """Request payload for registering a new user account."""

    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    full_name: str = Field(min_length=1, max_length=100)
    nickname: str = Field(min_length=1, max_length=50)
    gender: str = Field(min_length=1, max_length=10)
    password: str = Field(min_length=6, max_length=72)

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Request payload for authenticating an existing user via email."""

    email: str = Field(min_length=1)
    password: str = Field(min_length=1)

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Response payload containing the JWT access token."""

    access_token: str
    token_type: str = "bearer"
    full_name: str
    nickname: str
    preferred_greeting: str

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    """Decoded JWT token payload for internal use."""

    sub: str          # user_id as string
    email: str
    full_name: str
    nickname: str
    preferred_greeting: str
    db_path: str      # absolute path to the user's personal database

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """Payload for changing user password."""

    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6, max_length=72)


class ProfileResponse(BaseModel):
    """Response payload for user profile details."""

    id: int
    email: str
    full_name: str
    nickname: str
    preferred_greeting: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class DeleteAccountRequest(BaseModel):
    """Payload for account deletion confirmation."""

    password: str = Field(min_length=1)

class UpdateProfileRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    nickname: str = Field(min_length=1, max_length=50)
    preferred_greeting: str | None = None

class ForgotPasswordRequest(BaseModel):
    email: str = Field(min_length=1)

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=6, max_length=72)
