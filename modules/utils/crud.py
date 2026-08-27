"""
Generic Session State CRUD Manager for imagine
Path: Modules/utils/crud.py
App: imagine
"""

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from Modules.utils.mock_data import init_mock_data


def _ensure_initialized(key: str) -> None:
    """Ensures mock data is present in session state before querying."""
    if key not in st.session_state:
        init_mock_data()


def get_all(key: str) -> List[Dict[str, Any]]:
    """Returns all records for a given session state entity key."""
    _ensure_initialized(key)
    return st.session_state.get(key, [])


def get_by_id(key: str, item_id: Any, id_field: str = "id") -> Optional[Dict[str, Any]]:
    """Fetches a single record by ID."""
    items = get_all(key)
    for item in items:
        if str(item.get(id_field)) == str(item_id):
            return item
    return None


def filter_items(key: str, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
    """Filters entity records using a custom evaluation function."""
    items = get_all(key)
    return [item for item in items if predicate(item)]


def create_item(key: str, item_data: Dict[str, Any], id_field: str = "id") -> Dict[str, Any]:
    """Adds a new record to the target entity collection in st.session_state."""
    _ensure_initialized(key)

    new_item = dict(item_data)
    if "created_at" not in new_item:
        new_item["created_at"] = datetime.now(timezone.utc).isoformat()

    st.session_state[key].append(new_item)
    return new_item


def update_item(
    key: str,
    item_id: Any,
    updated_data: Dict[str, Any],
    id_field: str = "id",
) -> bool:
    """Updates an existing item by key and ID in place."""
    _ensure_initialized(key)
    items = st.session_state.get(key, [])

    for i, item in enumerate(items):
        if str(item.get(id_field)) == str(item_id):
            # Preserve original ID and merge changes
            merged_item = {**item, **updated_data, id_field: item[id_field]}
            merged_item["updated_at"] = datetime.now(timezone.utc).isoformat()
            st.session_state[key][i] = merged_item
            return True

    return False


def delete_item(key: str, item_id: Any, id_field: str = "id") -> bool:
    """Removes a record from st.session_state by ID."""
    _ensure_initialized(key)
    initial_count = len(st.session_state[key])
    st.session_state[key] = [
        item for item in st.session_state[key] if str(item.get(id_field)) != str(item_id)
    ]
    return len(st.session_state[key]) < initial_count
