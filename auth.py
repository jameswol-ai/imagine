import streamlit as st

# Define role permissions for actions
EXPORT_ALLOWED_ROLES = {"Admin", "Project Manager", "Lead Engineer"}

def check_permission(required_roles: set) -> bool:
    """Verifies if the current logged-in user has an authorized role."""
    user = st.session_state.get("user")
    if not user:
        return False
    return user.get("role") in required_roles
