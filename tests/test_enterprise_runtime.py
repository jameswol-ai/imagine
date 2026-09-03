"""Tests for the shared enterprise module runtime."""

from __future__ import annotations

from enum import Enum

from modules.enterprise_runtime import _active_route, _records, render_module
from modules.ui_sanitizer import strip_emoji


class SampleStatus(str, Enum):
    active = "active"
    on_hold = "on_hold"


def test_strip_emoji_removes_common_ui_glyphs() -> None:
    assert strip_emoji("Hello 📐 World") == "Hello  World"
    assert strip_emoji(["A 🏠", "B ✨"]) == ["A", "B"]


def test_strip_emoji_preserves_enum_instances() -> None:
    value = SampleStatus.on_hold
    assert strip_emoji(value) is value
    assert strip_emoji([SampleStatus.active])[0] is SampleStatus.active


def test_workspace_storage_is_session_backed() -> None:
    import streamlit as st

    st.session_state["active_route"] = "Test Module"
    records = _records(_active_route())
    records.clear()
    records.append({"name": "Example"})
    assert _records("Test Module")[0]["name"] == "Example"


def test_runtime_renderer_is_callable() -> None:
    assert callable(render_module)
