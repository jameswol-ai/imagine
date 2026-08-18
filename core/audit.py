"""
System Audit Logging
"""

from datetime import datetime

from core.database import execute_query


def log_event(
        username,
        action,
        entity="system"
):

    execute_query(
        """
        INSERT INTO audit_logs
        (
            username,
            entity,
            action,
            created_at
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            username,
            entity,
            action,
            datetime.utcnow()
        )
    )
