import hashlib
import uuid

from core.database import execute_query


def hash_password(
        password,
        salt):

    return hashlib.sha256(
        (password + salt).encode()
    ).hexdigest()


def authenticate_user(
        username,
        password):

    row = execute_query(
        """
        SELECT password_hash,
               salt,
               role
        FROM users
        WHERE username=?
        """,
        (username,),
        fetch="one"
    )

    if not row:
        return False, None

    password_hash, salt, role = row

    if hash_password(password, salt) == password_hash:
        return True, role

    return False, None


def register_user(
        username,
        password,
        role,
        email=""):

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
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            password_hash,
            salt,
            role,
            email
        )
    )
