"""Regression tests for the lightweight Streamlit CRUD repository."""
from __future__ import annotations

import streamlit as st

from modules.utils.crud import CRUDService


def test_crud_service_create_read_update_delete() -> None:
    key = "_test_crud_service"
    st.session_state.pop(key, None)

    created = CRUDService.create(key, {"id": "A-001", "name": "Column C-101"})
    assert created["id"] == "A-001"
    assert CRUDService.get_all(key) == [created]
    assert CRUDService.get_by_id(key, "A-001") == created

    assert CRUDService.update(key, "A-001", {"status": "PASS"}) is True
    assert CRUDService.get_by_id(key, "A-001")["status"] == "PASS"

    assert CRUDService.delete(key, "A-001") is True
    assert CRUDService.get_all(key) == []
    assert CRUDService.get_by_id(key, "A-001") is None

    st.session_state.pop(key, None)


def test_crud_service_missing_update_and_delete_are_safe() -> None:
    key = "_test_crud_service_missing"
    st.session_state.pop(key, None)
    assert CRUDService.update(key, "missing", {"status": "REVIEW"}) is False
    assert CRUDService.delete(key, "missing") is False
    st.session_state.pop(key, None)
