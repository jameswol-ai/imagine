"""
IMAGINE
Application Settings
"""

from __future__ import annotations

import os


class Settings:
    """Application configuration.

    Environment variables override the defaults.
    This implementation intentionally avoids making the
    database layer depend on pydantic-settings just to import.
    """

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "IMAGINE",
    )

    DEBUG: bool = os.getenv(
        "DEBUG",
        "false",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    API_V1_PREFIX: str = os.getenv(
        "API_V1_PREFIX",
        "/api/v1",
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key",
    )

    ALGORITHM: str = os.getenv(
        "ALGORITHM",
        "HS256",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "10080",
        )
    )

    DB_USER: str = os.getenv(
        "DB_USER",
        "postgres",
    )

    DB_PASSWORD: str = os.getenv(
        "DB_PASSWORD",
        "postgres",
    )

    DB_HOST: str = os.getenv(
        "DB_HOST",
        "localhost",
    )

    DB_PORT: int = int(
        os.getenv(
            "DB_PORT",
            "5432",
        )
    )

    DB_NAME: str = os.getenv(
        "DB_NAME",
        "imagine",
    )

    @property
    def DATABASE_URL(self) -> str:
        """Return the asynchronous PostgreSQL URL."""

        return (
            "postgresql+asyncpg://"
            f"{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )


settings = Settings()