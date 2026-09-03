"""Database bootstrap utilities for IMAGINE."""
from __future__ import annotations

from typing import Any

from sqlalchemy import inspect, text

from database.connection import Base, DATABASE_URL, engine


def _ensure_bim_legacy_columns() -> None:
    """Add BIM columns introduced after the original BIM tables.

    This is deliberately additive and nullable so existing deployments are not
    forced through destructive migrations. Production schema evolution should
    still be captured by a proper migration system when one is introduced.
    """
    additions = {
        "buildings": {
            "code": "VARCHAR",
            "height": "FLOAT",
            "typology": "VARCHAR",
            "status": "VARCHAR",
        },
        "storeys": {
            "code": "VARCHAR",
            "elevation": "FLOAT",
            "description": "VARCHAR",
        },
        "spaces": {
            "code": "VARCHAR",
            "capacity": "INTEGER",
        },
        "elements": {
            "storey_id": "VARCHAR",
            "code": "VARCHAR",
            "type_name": "VARCHAR",
            "status": "VARCHAR",
            "guid": "VARCHAR",
        },
    }

    with engine.begin() as connection:
        inspector = inspect(connection)
        for table_name, columns in additions.items():
            if table_name not in inspector.get_table_names():
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_type in columns.items():
                if column_name not in existing:
                    connection.execute(
                        text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type}')
                    )


def ensure_schema() -> None:
    """Create missing registered tables and reconcile additive BIM columns."""
    import projects.model_registry  # noqa: F401
    from database.models.module_workspace import ModuleWorkspaceRecord  # noqa: F401
    from database.models.project_file import ProjectFileRecord  # noqa: F401

    Base.metadata.create_all(bind=engine, checkfirst=True)
    _ensure_bim_legacy_columns()


def database_health() -> dict[str, Any]:
    """Return a small, safe database health report for the UI."""
    required = {
        "projects",
        "approvals",
        "revisions",
        "workflows",
        "module_workspace_records",
        "project_files",
        "buildings",
        "storeys",
        "spaces",
        "elements",
        "ifc_models",
        "cobie_assets",
        "digital_twins",
    }
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            inspector = inspect(connection)
            tables = set(inspector.get_table_names())
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
            "required_tables": sorted(required),
            "missing_tables": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


__all__ = ["ensure_schema", "database_health"]
