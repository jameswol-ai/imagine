"""Shared BIM state helpers and data contracts."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import streamlit as st
from modules.utils.crud import CRUDService

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


def records(key: str) -> list[dict]:
    return CRUDService.get_all(key)


def save(key: str, record: dict) -> None:
    CRUDService.create(key, record)


def delete(key: str, record_id: str) -> None:
    CRUDService.delete(key, record_id)


def active_project() -> str:
    return str(st.session_state.get("active_project_id", ""))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def asdict_element(element: BIMElement) -> dict:
    return asdict(element)


def seed_if_empty(key: str, seed: list[dict]) -> list[dict]:
    data = records(key)
    if not data and seed:
        st.session_state[key] = seed
        data = seed
    return data
