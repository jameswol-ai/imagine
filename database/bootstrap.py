"""
Database bootstrap utilities for IMAGINE.

The Streamlit application can safely call ensure_schema() on startup or
before a database-backed module is rendered. The function imports the
canonical model registry first, which ensures relationship targets are
registered before SQLAlchemy creates/configures mappers.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import inspect, text

from database.connection import Base, DATABASE_URL, engine


def ensure_schema() -> None:
    """Create missing registered tables without dropping existing data."""
    # Importing this registry is intentional and must happen before
    # metadata.create_all so Project/Approval/Revision relationships resolve.
    import projects.model_registry  # noqa: F401

    Base.metadata.create_all(bind=engine, checkfirst=True)


def database_health() -> dict[str, Any]:
    """Return a small, safe database health report for the UI."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

            inspector = inspect(connection)
            tables = set(inspector.get_table_names())

        required = {"projects", "approvals", "revisions"}
        return {
            "ok": True,
            "configured_url": DATABASE_URL,
            "driver": engine.url.drivername,
            "required_tables": sorted(required),
            "missing_tables": sorted(required - tables),
        }
    except Exception as exc:
        return {
            "ok": False,
            "configured_url": DATABASE_URL,
            "driver": engine.url.drivername,
            "required_tables": ["projects", "approvals", "revisions"],
            "missing_tables": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


__all__ = ["ensure_schema", "database_health"]
