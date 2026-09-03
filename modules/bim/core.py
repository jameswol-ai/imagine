"""Shared BIM state helpers and project-scoped data contracts."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import streamlit as st
from sqlalchemy import select

from database.connection import SessionLocal
from modules.utils.crud import CRUDService
from .persistence import available as persistence_available, load as db_load, create as db_create


@dataclass(frozen=True)
class BIMElement:
    id: str
    building_id: str
    storey_id: str
    category: str
    name: str
    type_name: str
    quantity: float = 1.0
    unit: str = "item"
    status: str = "Design"
    guid: str = ""


def project_options() -> dict[str, str]:
    """Return real Projects as UUID -> display-name options."""
    try:
        from projects.projects.models import Project

        with SessionLocal() as db:
            projects = db.scalars(select(Project).order_by(Project.name)).all()
        return {str(project.id): project.name for project in projects}
    except Exception:
        return {}


def active_project() -> str:
    """Return the selected project, defaulting to the first real project."""
    current = str(st.session_state.get("active_project_id", ""))
    if current:
        return current

    options = project_options()
    if options:
        current = next(iter(options))
        st.session_state["active_project_id"] = current
    return current


def set_active_project(project_id: str) -> None:
    st.session_state["active_project_id"] = str(project_id)
    for key in ("bim_buildings", "bim_storeys", "bim_spaces", "bim_elements"):
        st.session_state.pop(key, None)


def records(key: str) -> list[dict[str, Any]]:
    """Load project-scoped records when possible, otherwise use session fallback."""
    pid = active_project()
    if pid and persistence_available():
        loaded = db_load(key, pid)
        if loaded:
            return loaded
    return CRUDService.get_all(key)


def save(key: str, record: dict[str, Any]) -> None:
    """Persist a BIM record when an active project exists, with session fallback."""
    pid = active_project()
    if pid and persistence_available():
        try:
            db_create(key, record, pid)
            return
        except Exception as exc:
            st.warning(f"Database persistence unavailable for this BIM record: {exc}")
    CRUDService.create(key, record)


def delete(key: str, record_id: str) -> None:
    """Delete from the compatibility UI store until destructive DB APIs are hardened."""
    CRUDService.delete(key, record_id)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def asdict_element(element: BIMElement) -> dict[str, Any]:
    return asdict(element)


def seed_if_empty(key: str, seed: list[dict]) -> list[dict]:
    data = records(key)
    if not data and seed:
        st.session_state[key] = seed
        data = seed
    return data


__all__ = [
    "BIMElement",
    "active_project",
    "set_active_project",
    "project_options",
    "records",
    "save",
    "delete",
    "utc_now",
    "asdict_element",
    "seed_if_empty",
]
