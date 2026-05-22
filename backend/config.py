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
    database_url: str = Field(
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    gemini_api_key: str = Field(
        validation_alias=AliasChoices("GEMINI_API_KEY"),
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
