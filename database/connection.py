"""
IMAGINE database connection.

Central SQLAlchemy database configuration.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings


# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("SQLALCHEMY_DATABASE_URL")
    or settings.database_url
)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./imagine.db"


# ============================================================
# SYNCHRONOUS DATABASE
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


# ============================================================
# ASYNCHRONOUS DATABASE
# ============================================================

def _async_database_url(url: str) -> str:
    """
    Convert the configured synchronous SQLAlchemy URL into
    the corresponding async-driver URL.
    """

    if url.startswith("sqlite:///"):
        return url.replace(
            "sqlite:///",
            "sqlite+aiosqlite:///",
            1,
        )

    if url.startswith("postgresql://"):
        return url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )

    if url.startswith("postgres://"):
        return url.replace(
            "postgres://",
            "postgresql+asyncpg://",
            1,
        )

    if url.startswith("mysql://"):
        return url.replace(
            "mysql://",
            "mysql+aiomysql://",
            1,
        )

    return url


ASYNC_DATABASE_URL = _async_database_url(
    DATABASE_URL
)


async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    future=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================================
# ORM BASE
# ============================================================

Base = declarative_base()


# ============================================================
# SYNCHRONOUS DEPENDENCY
# ============================================================

def get_db():
    """Yield a synchronous database session."""

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()