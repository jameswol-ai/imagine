"""
Authentication Service
"""

import hashlib
import uuid

from core.database import execute_query


def hash_password(
        password: str,
        salt: str
) -> str:

    return hashlib.sha256(
        f"{password}{salt}".encode(
            "utf-8"
        )
    ).hexdigest()


def authenticate_user(
        username,
        password
):

    row = execute_query(
        """
        SELECT
            password_hash,
            salt,
            role
        FROM users
        WHERE username = ?
        """,
        (username,),
        fetch="one"
    )

    if not row:
        return False, None

    db_hash, salt, role = row

    password_hash = hash_password(
        password,
        salt
    )

    if password_hash == db_hash:
        return True, role

    return False, None


def register_user(
        username,
        password,
        role,
        email=""
):

    salt = uuid.uuid4().hex

    password_hash = hash_password(
        password,
        salt
    )

    execute_query(
        """
        INSERT INTO users
        (
            username,
            password_hash,
            salt,
            role,
            email
        )
        VALUES
        (?, ?, ?, ?, ?)
        """,
        (
            username,
            password_hash,
            salt,
            role,
            email
        )
    )

    return True


def generate_uuid():

    return str(
        uuid.uuid4()
    )
