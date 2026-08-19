"""
IMAGINE application settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    app_name: str = os.getenv(
        "IMAGINE_APP_NAME",
        "IMAGINE",
    )

    environment: str = os.getenv(
        "IMAGINE_ENVIRONMENT",
        "development",
    )

    database_url: str = os.getenv(
        "DATABASE_URL",
        "",
    )

    debug: bool = os.getenv(
        "IMAGINE_DEBUG",
        "false",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


settings = Settings()