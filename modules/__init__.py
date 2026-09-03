"""IMAGINE Streamlit module package."""

# Install before any module renderer is imported. Python initializes the
# package before resolving modules such as modules.enterprise_registry.
from modules.ui_sanitizer import install_emoji_free_ui

install_emoji_free_ui()

__all__ = ["install_emoji_free_ui"]
