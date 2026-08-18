"""
IMAGINE Enterprise Platform
Application Settings
"""

import os


class Settings:

    # ---------------------------------------------------
    # Application
    # ---------------------------------------------------

    APP_NAME = "IMAGINE"
    APP_VERSION = "24.1"

    DEBUG = os.getenv(
        "DEBUG",
        "False"
    ).lower() == "true"

    # ---------------------------------------------------
    # Database
    # ---------------------------------------------------

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        ""
    )

    SQLITE_DB = os.getenv(
        "SQLITE_DB",
        "imagine_platform.db"
    )

    # ---------------------------------------------------
    # Security
    # ---------------------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-in-production"
    )

    PASSWORD_MIN_LENGTH = 8

    # ---------------------------------------------------
    # User Roles
    # ---------------------------------------------------

    ROLES = [
        "Admin",
        "Project Lead",
        "Architect",
        "Structural Engineer",
        "MEP Engineer",
        "Quantity Surveyor",
        "Viewer"
    ]

    APPROVAL_ROLES = [
        "Admin",
        "Project Lead"
    ]

    # ---------------------------------------------------
    # BIM
    # ---------------------------------------------------

    IFC_VERSION = "IFC4"

    # ---------------------------------------------------
    # Currency Defaults
    # ---------------------------------------------------

    DEFAULT_COUNTRY = "Uganda"

    DEFAULT_CURRENCY = "UGX"


settings = Settings()
