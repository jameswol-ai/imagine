import bcrypt
import streamlit as st

conn = st.connection("postgresql", type="sql")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def authenticate_user(username: str, password: str) -> dict | None:
    """Fetches user from PostgreSQL and verifies credentials."""
    query = "SELECT id, username, password_hash, role FROM users WHERE username = :username;"
    
    # ttl=0 ensures fresh lookup without caching old auth results
    df = conn.query(query, params={"username": username}, ttl=0)
    
    if df.empty:
        return None
        
    user_record = df.iloc[0].to_dict()
    
    if verify_password(password, user_record["password_hash"]):
        return {
            "id": user_record["id"],
            "username": user_record["username"],
            "role": user_record["role"]
        }
    return None
