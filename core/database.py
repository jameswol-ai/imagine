import sqlite3
import os

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


def get_db_connection():
    pg_url = os.getenv("DATABASE_URL")

    if HAS_POSTGRES and pg_url:
        return psycopg2.connect(pg_url), "postgres"

    return sqlite3.connect(
        "imagine_platform.db",
        check_same_thread=False
    ), "sqlite"


def execute_query(
        query,
        params=(),
        fetch=None):

    conn, db_type = get_db_connection()

    if db_type == "postgres":
        query = query.replace("?", "%s")

    cursor = conn.cursor()

    try:
        cursor.execute(query, params)

        result = None

        if fetch == "one":
            result = cursor.fetchone()

        elif fetch == "all":
            result = cursor.fetchall()

        conn.commit()

        return result

    finally:
        cursor.close()
        conn.close()
