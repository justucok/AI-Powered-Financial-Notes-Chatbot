from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(
        default="AI Financial Notes Chatbot",
        validation_alias=AliasChoices("APP_NAME"),
    )
    api_v1_prefix: str = Field(
        default="/api/v1",
        validation_alias=AliasChoices("API_V1_PREFIX"),
    )
    secret_key: str = Field(
        validation_alias=AliasChoices("SECRET_KEY"),
    )
    access_token_expire_days: int = Field(
        default=7,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_DAYS"),
    )
    gemini_api_key: str = Field(
        validation_alias=AliasChoices("GEMINI_API_KEY"),
    )
    database_url: str = Field(
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    allowed_origins: str = Field(
        default="*",
        validation_alias=AliasChoices("ALLOWED_ORIGINS"),
    )
    smtp_server: str = Field(
        default="smtp.gmail.com",
        validation_alias=AliasChoices("SMTP_SERVER"),
    )
    smtp_port: int = Field(
        default=587,
        validation_alias=AliasChoices("SMTP_PORT"),
    )
    smtp_username: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SMTP_USERNAME"),
    )
    smtp_password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SMTP_PASSWORD"),
    )
    frontend_url: str = Field(
        default="http://localhost:5173",
        validation_alias=AliasChoices("FRONTEND_URL"),
    )

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
