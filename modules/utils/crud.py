"""Shared Streamlit CRUD helpers.

The module provides a small session-state repository used by lightweight
workspace pages. It deliberately keeps persistence concerns out of the UI
layer while giving modules a stable CRUDService contract.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st


class CRUDService:
    """Session-state CRUD repository used by interactive IMAGINE modules."""

    @staticmethod
    def _data(data_key: str) -> List[Dict[str, Any]]:
        data = st.session_state.get(data_key)
        if data is None:
            data = []
            st.session_state[data_key] = data
        if not isinstance(data, list):
            raise TypeError(f"Session state '{data_key}' must contain a list.")
        return data

    @classmethod
    def get_all(cls, data_key: str) -> List[Dict[str, Any]]:
        """Return all records for a session-state collection."""
        return cls._data(data_key)

    @classmethod
    def get_by_id(
        cls,
        data_key: str,
        record_id: Any,
        id_field: str = "id",
    ) -> Optional[Dict[str, Any]]:
        """Return one record by identifier, or ``None`` when absent."""
        return next(
            (item for item in cls._data(data_key) if item.get(id_field) == record_id),
            None,
        )

    @classmethod
    def create(cls, data_key: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Append a record and return the stored dictionary."""
        if not isinstance(record, dict):
            raise TypeError("CRUDService.create expects a dictionary record.")
        data = cls._data(data_key)
        stored = dict(record)
        data.append(stored)
        st.session_state[data_key] = data
        return stored

    @classmethod
    def update(
        cls,
        data_key: str,
        record_id: Any,
        updated_fields: Dict[str, Any],
        id_field: str = "id",
    ) -> bool:
        """Update an existing record and return whether it was found."""
        if not isinstance(updated_fields, dict):
            raise TypeError("CRUDService.update expects a dictionary of fields.")
        for item in cls._data(data_key):
            if item.get(id_field) == record_id:
                item.update(updated_fields)
                return True
        return False

    @classmethod
    def delete(
        cls,
        data_key: str,
        record_id: Any,
        id_field: str = "id",
    ) -> bool:
        """Delete an existing record and return whether it was removed."""
        data = cls._data(data_key)
        original_length = len(data)
        st.session_state[data_key] = [
            item for item in data if item.get(id_field) != record_id
        ]
        return len(st.session_state[data_key]) != original_length


def crud_table(
    data_key,
    item_name,
    endpoint,
    id_field="id",
    display_fields=None,
    edit_fields=None,
    add_fields=None,
):
    """Render a backwards-compatible editable session-state table."""
    del endpoint
    data = CRUDService.get_all(data_key)
    if not data:
        st.info(f"No {item_name} data available.")
        return
    if display_fields is None:
        display_fields = list(data[0].keys()) if data else []
    for item in data:
        cols = st.columns([2] * len(display_fields) + [1, 1])
        for i, field in enumerate(display_fields):
            with cols[i]:
                st.write(item.get(field, ""))
        with cols[-2]:
            if st.button("Edit", key=f"edit_{item_name}_{item[id_field]}"):
                st.session_state[f"editing_{item_name}"] = item
        with cols[-1]:
            if st.button("Delete", key=f"del_{item_name}_{item[id_field]}"):
                st.session_state[f"confirm_{item_name}_{item[id_field]}"] = True
                st.rerun()
        editing_key = f"editing_{item_name}"
        if st.session_state.get(editing_key) is not None:
            editing_item = st.session_state[editing_key]
            if isinstance(editing_item, dict) and editing_item.get(id_field) == item.get(id_field):
                with st.expander(f"Edit {item.get('name', item.get('level', item[id_field]))}", expanded=True):
                    with st.form(key=f"edit_{item_name}_form_{item[id_field]}"):
                        edit_values = {}
                        fields = edit_fields or {field: "text" for field in display_fields}
                        for field, input_type in fields.items():
                            if input_type == "text":
                                edit_values[field] = st.text_input(field.capitalize(), value=str(item.get(field, "")))
                            elif input_type == "number":
                                edit_values[field] = st.number_input(field.capitalize(), value=float(item.get(field, 0.0)), step=0.1)
                            elif input_type == "select":
                                options = item.get("options", [])
                                current = item.get(field, options[0] if options else "")
                                edit_values[field] = st.selectbox(field.capitalize(), options, index=options.index(current) if current in options else 0)
                        if st.form_submit_button("Update"):
                            CRUDService.update(data_key, item[id_field], edit_values, id_field=id_field)
                            st.session_state[editing_key] = None
                            st.success(f"{item_name.capitalize()} updated.")
                            st.rerun()
                if st.button("Cancel", key=f"cancel_{item_name}_edit_{item[id_field]}"):
                    st.session_state[editing_key] = None
                    st.rerun()
        confirm_key = f"confirm_{item_name}_{item[id_field]}"
        if st.session_state.get(confirm_key):
            st.warning(f"Delete {item_name} '{item[id_field]}'?")
            yes, no = st.columns(2)
            with yes:
                if st.button("Confirm", key=f"confirm_yes_{item_name}_{item[id_field]}"):
                    CRUDService.delete(data_key, item[id_field], id_field=id_field)
                    st.session_state[confirm_key] = False
                    st.rerun()
            with no:
                if st.button("Cancel", key=f"confirm_no_{item_name}_{item[id_field]}"):
                    st.session_state[confirm_key] = False
                    st.rerun()
    with st.expander(f"Add New {item_name.capitalize()}"):
        with st.form(key=f"new_{item_name}_form"):
            add_values = {}
            fields = add_fields or edit_fields or {field: "text" for field in display_fields}
            for field, input_type in fields.items():
                if input_type == "text":
                    add_values[field] = st.text_input(field.capitalize())
                elif input_type == "number":
                    add_values[field] = st.number_input(field.capitalize(), value=0.0, step=0.1)
                elif input_type == "select":
                    options = data[0].get("options", []) if data else []
                    add_values[field] = st.selectbox(field.capitalize(), options)
            if st.form_submit_button("Create"):
                if id_field not in add_values:
                    numeric_ids = [d.get(id_field) for d in data if isinstance(d.get(id_field), (int, float))]
                    add_values[id_field] = int(max(numeric_ids, default=0)) + 1
                CRUDService.create(data_key, add_values)
                st.success(f"{item_name.capitalize()} created.")
                st.rerun()
