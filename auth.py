import bcrypt
import streamlit as st
from sqlalchemy import text

conn = st.connection("postgresql", type="sql")

def update_user_password(username: str, current_pw: str, new_pw: str) -> tuple[bool, str]:
    """Verifies existing credentials and updates to a new bcrypt hash."""
    # 1. Fetch stored hash
    df = conn.query(
        "SELECT password_hash FROM users WHERE username = :username;",
        params={"username": username},
        ttl=0
    )
    
    if df.empty:
        return False, "User account not found."
    
    stored_hash = df.iloc[0]["password_hash"]
    
    # 2. Verify current password
    if not bcrypt.checkpw(current_pw.encode('utf-8'), stored_hash.encode('utf-8')):
        return False, "Current password is incorrect."
    
    # 3. Generate new bcrypt hash
    salt = bcrypt.gensalt(rounds=12)
    new_hash = bcrypt.hashpw(new_pw.encode('utf-8'), salt).decode('utf-8')
    
    # 4. Perform atomic update in DB session
    try:
        with conn.session as session:
            session.execute(
                text("UPDATE users SET password_hash = :new_hash WHERE username = :username;"),
                {"new_hash": new_hash, "username": username}
            )
            session.commit()
        return True, "Password updated successfully!"
    except Exception as e:
        return False, f"Database update failed: {e}"
