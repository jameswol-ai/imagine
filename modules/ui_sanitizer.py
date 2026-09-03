"""Centralized Streamlit UI text sanitizer.

IMAGINE uses a consistent enterprise UI without emoji glyphs. Existing
specialist modules can keep their internal labels unchanged while this
adapter strips emoji characters from all common Streamlit text/widget APIs
when the application shell is loaded.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from functools import wraps
from typing import Any

import streamlit as st


_EMOJI_RE = re.compile(
    "["
    "\\U0001F1E0-\\U0001F1FF"
    "\\U0001F300-\\U0001F5FF"
    "\\U0001F600-\\U0001F64F"
    "\\U0001F680-\\U0001F6FF"
    "\\U0001F700-\\U0001F77F"
    "\\U0001F780-\\U0001F7FF"
    "\\U0001F800-\\U0001F8FF"
    "\\U0001F900-\\U0001F9FF"
    "\\U0001FA00-\\U0001FAFF"
    "\\u2600-\\u27BF"
    "]+",
    flags=re.UNICODE,
)



def strip_emoji(value: Any) -> Any:
    if isinstance(value, str):
        return _EMOJI_RE.sub("", value).strip()
    if isinstance(value, list):
        return [strip_emoji(item) for item in value]
    if isinstance(value, tuple):
        return tuple(strip_emoji(item) for item in value)
    if isinstance(value, dict):
        return {strip_emoji(key): strip_emoji(item) for key, item in value.items()}
    return value


_PATCHED = False


def _wrap_method(name: str) -> None:
    original = getattr(st, name, None)
    if original is None or getattr(original, "_imagine_emoji_free", False):
        return

    @wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        args = tuple(strip_emoji(value) for value in args)
        kwargs = {key: strip_emoji(value) for key, value in kwargs.items()}
        return original(*args, **kwargs)

    wrapped._imagine_emoji_free = True
    setattr(st, name, wrapped)



def install_emoji_free_ui() -> None:
    global _PATCHED
    if _PATCHED:
        return

    for name in (
        "title",
        "header",
        "subheader",
        "markdown",
        "write",
        "caption",
        "text",
        "code",
        "info",
        "success",
        "warning",
        "error",
        "metric",
        "button",
        "link_button",
        "download_button",
        "checkbox",
        "radio",
        "selectbox",
        "multiselect",
        "text_input",
        "text_area",
        "number_input",
        "date_input",
        "time_input",
        "file_uploader",
        "tabs",
        "expander",
    ):
        _wrap_method(name)

    _PATCHED = True


__all__ = ["install_emoji_free_ui", "strip_emoji"]
