"""
IMAGINE database connection.

Central SQLAlchemy database configuration shared by Streamlit, API and
background services.
"""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings


def _streamlit_secret_database_url() -> str | None:
    """Read DATABASE_URL from Streamlit secrets when available."""
    try:
        import streamlit as st

        value: Any = st.secrets.get("DATABASE_URL")
        if value:
            return str(value).strip()

        database_section = st.secrets.get("database")
        if isinstance(database_section, dict):
            value = database_section.get("url")
            if value:
                return str(value).strip()
    except Exception:
        pass

    return None


DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("SQLALCHEMY_DATABASE_URL")
    or _streamlit_secret_database_url()
    or settings.database_url
    or "sqlite:///./imagine.db"
)


connect_args: dict[str, Any] = {}
engine_kwargs: dict[str, Any] = {"future": True}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 5,
            "pool_recycle": 1800,
        }
    )

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def _async_database_url(url: str) -> str:
    """Convert a supported SQLAlchemy URL to an async-driver URL."""
    replacements = (
        ("postgresql+psycopg2://", "postgresql+asyncpg://"),
        ("postgresql://", "postgresql+asyncpg://"),
        ("postgres://", "postgresql+asyncpg://"),
        ("mysql+pymysql://", "mysql+aiomysql://"),
        ("mysql://", "mysql+aiomysql://"),
        ("sqlite:///", "sqlite+aiosqlite:///"),
    )

    for source, target in replacements:
        if url.startswith(source):
            return url.replace(source, target, 1)

    return url


ASYNC_DATABASE_URL = _async_database_url(DATABASE_URL)
async_engine_kwargs: dict[str, Any] = {"future": True}

if not ASYNC_DATABASE_URL.startswith("sqlite"):
    async_engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 5,
            "pool_recycle": 1800,
        }
    )

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    **async_engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


Base = declarative_base()


def get_db():
    """Yield a synchronous database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Yield an asynchronous database session."""
    async with AsyncSessionLocal() as db:
        yield db
