"""
IMAGINE audit record model.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class AuditRecord(Base):
    """
    Records application actions performed by users.
    """

    __tablename__ = "audit_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    resource: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # "metadata" is reserved by SQLAlchemy's Declarative API.
    #
    # Keep the database column named "metadata", but expose
    # it to Python as "metadata_json".
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="audit_records",
    )