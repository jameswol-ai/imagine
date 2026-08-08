import bcrypt
import streamlit as st
from sqlalchemy import text

conn = st.connection("postgresql", type="sql")

def get_all_users():
    """Fetches full user roster for administrative view."""
    return conn.query("SELECT id, username, role, created_at FROM users ORDER BY username ASC;", ttl=0)

def admin_reset_password(username: str, new_password: str) -> tuple[bool, str]:
    """Generates a new bcrypt hash and overrides the specified user's password."""
    salt = bcrypt.gensalt(rounds=12)
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
    try:
        with conn.session as session:
            session.execute(
                text("UPDATE users SET password_hash = :hash WHERE username = :username;"),
                {"hash": new_hash, "username": username}
            )
            session.commit()
        return True, f"Password successfully updated for '{username}'."
    except Exception as e:
        return False, f"Failed to reset password: {e}"

def admin_update_role(username: str, new_role: str) -> tuple[bool, str]:
    """Updates the user role in PostgreSQL."""
    try:
        with conn.session as session:
            session.execute(
                text("UPDATE users SET role = :role WHERE username = :username;"),
                {"role": new_role, "username": username}
            )
            session.commit()
        return True, f"Role for '{username}' updated to '{new_role}'."
    except Exception as e:
        return False, f"Failed to update role: {e}"
