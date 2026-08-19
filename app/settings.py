"""
IMAGINE
Application Settings
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "IMAGINE"

    DEBUG: bool = False

    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str = Field(
        default="your-secret-key"
    )

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DB_USER: str = "postgres"

    DB_PASSWORD: str = "postgres"

    DB_HOST: str = "localhost"

    DB_PORT: int = 5432

    DB_NAME: str = "imagine"

    @property
    def DATABASE_URL(self) -> str:
        """Return the asynchronous PostgreSQL connection URL."""

        return (
            "postgresql+asyncpg://"
            f"{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )


settings = Settings()