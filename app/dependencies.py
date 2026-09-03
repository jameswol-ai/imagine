"""FastAPI dependency helpers."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Generator

from database.connection import get_db


def get_db_dependency() -> Generator:
    db = get_db()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app):
    """Application lifecycle hook.

    Database initialization is intentionally best-effort so the API can still
    start in environments where DATABASE_URL is not configured yet.
    """
    try:
        from database.bootstrap import database_health
        database_health()
    except Exception:
        pass
    yield
