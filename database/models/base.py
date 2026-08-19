"""
IMAGINE shared database model base classes.
"""

from __future__ import annotations

import uuid

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class BaseModel(Base):
    """
    Shared model fields.

    Models requiring common audit timestamps and creator
    information can inherit from this class.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[object] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[object | None] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True,
    )

    created_by: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    updated_by: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )