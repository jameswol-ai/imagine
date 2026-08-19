"""
IMAGINE database connection and SQLAlchemy configuration.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.settings import settings


# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = settings.database_url


# ============================================================
# ENGINE OPTIONS
# ============================================================

connect_args: dict[str, object] = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False


# ============================================================
# ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ============================================================
# DECLARATIVE BASE
# ============================================================


class Base(DeclarativeBase):
    """
    Shared SQLAlchemy declarative base.

    All database models should inherit from this Base,
    directly or through BaseModel.
    """

    pass


# ============================================================
# SESSION DEPENDENCY
# ============================================================


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session.

    The session is always closed after use.
    """

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()