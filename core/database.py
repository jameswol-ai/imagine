"""
Database Connection Layer
"""

import sqlite3

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

from core.settings import settings


def get_db_connection():

    if HAS_POSTGRES and settings.DATABASE_URL:

        db_url = settings.DATABASE_URL

        if db_url.startswith("postgres://"):
            db_url = db_url.replace(
                "postgres://",
                "postgresql://",
                1
            )

        conn = psycopg2.connect(
            db_url,
            sslmode="require"
        )

        return conn, "postgres"

    conn = sqlite3.connect(
        settings.SQLITE_DB,
        check_same_thread=False
    )

    return conn, "sqlite"


def format_query(
        query: str,
        db_type: str
):

    if db_type == "postgres":
        return query.replace(
            "?",
            "%s"
        )

    return query


def execute_query(
        query,
        params=(),
        fetch=None
):

    conn, db_type = get_db_connection()

    query = format_query(
        query,
        db_type
    )

    result = None

    try:

        cursor = conn.cursor()

        cursor.execute(
            query,
            params
        )

        if fetch == "one":
            result = cursor.fetchone()

        elif fetch == "all":
            result = cursor.fetchall()

        conn.commit()

        cursor.close()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

    return result
