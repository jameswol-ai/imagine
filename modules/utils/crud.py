"""
IMAGINE Platform Generic CRUD Operations
Path: modules/utils/crud.py
App: imagine
"""

from typing import Any, Dict, List, Optional
import streamlit as st


class CRUDService:
    """Generic CRUD operations manager acting on Streamlit session state."""

    @staticmethod
    def get_all(state_key: str) -> List[Dict[str, Any]]:
        """Retrieve all items stored under a specific session state key."""
        return st.session_state.get(state_key, [])

    @staticmethod
    def get_by_id(
        state_key: str, item_id: str, id_field: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """Find a single item by unique identifier."""
        items = CRUDService.get_all(state_key)
        for item in items:
            if str(item.get(id_field)) == str(item_id):
                return item
        return None

    @staticmethod
    def create(state_key: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Append a new record to the session state array."""
        if state_key not in st.session_state:
            st.session_state[state_key] = []
        st.session_state[state_key].append(record)
        return record

    @staticmethod
    def update(
        state_key: str,
        item_id: str,
        updated_fields: Dict[str, Any],
        id_field: str = "id",
    ) -> bool:
        """Update fields on an existing record."""
        items = CRUDService.get_all(state_key)
        for item in items:
            if str(item.get(id_field)) == str(item_id):
                item.update(updated_fields)
                return True
        return False

    @staticmethod
    def delete(state_key: str, item_id: str, id_field: str = "id") -> bool:
        """Remove a record by unique identifier."""
        if state_key in st.session_state:
            initial_len = len(st.session_state[state_key])
            st.session_state[state_key] = [
                item
                for item in st.session_state[state_key]
                if str(item.get(id_field)) != str(item_id)
            ]
            return len(st.session_state[state_key]) < initial_len
        return False
