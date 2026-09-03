"""IMAGINE specialist module package.

Package initialization is intentionally side-effect free. Streamlit UI
sanitization is installed explicitly by the application shell so importing a
specialist workspace cannot mutate Streamlit globally during lazy loading.
"""
from __future__ import annotations

__all__: list[str] = []
