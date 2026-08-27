"""
IMAGINE Platform — Generic Session-State CRUD Service
Path: modules/utils/crud.py
App: imagine
"""

from typing import Any, Dict, List, Optional
import streamlit as st


class CRUDService:
    """Utility service managing session state collections safely."""

    @staticmethod
    def get_all(key: str) -> List[Dict[str, Any]]:
        if key not in st.session_state:
            st.session_state[key] = []
        return st.session_state[key]

    @staticmethod
    def get_by_id(key: str, item_id: str, id_field: str = "id") -> Optional[Dict[str, Any]]:
        items = CRUDService.get_all(key)
        for item in items:
            if item.get(id_field) == item_id:
                return item
        return None

    @staticmethod
    def create(key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        items = CRUDService.get_all(key)
        items.append(data)
        st.session_state[key] = items
        return data

    @staticmethod
    def update(key: str, item_id: str, updated_fields: Dict[str, Any], id_field: str = "id") -> bool:
        items = CRUDService.get_all(key)
        for item in items:
            if item.get(id_field) == item_id:
                item.update(updated_fields)
                st.session_state[key] = items
                return True
        return False

    @staticmethod
    def delete(key: str, item_id: str, id_field: str = "id") -> bool:
        items = CRUDService.get_all(key)
        initial_len = len(items)
        items = [item for item in items if item.get(id_field) != item_id]
        st.session_state[key] = items
        return len(items) < initial_len
