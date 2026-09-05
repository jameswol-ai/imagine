"""Compatibility entrypoint for the IMAGINE Streamlit application.

The canonical application shell lives in ``streamlit_app.py``. Keeping this
small compatibility entrypoint means existing Streamlit Cloud deployments
that still target ``app.py`` use the same registry, navigation, diagnostics,
and lazy module loader instead of the legacy structural-only router.
"""
from __future__ import annotations

from streamlit_app import main


if __name__ == "__main__":
    main()
