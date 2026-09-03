"""Persistent project-file records for the IMAGINE platform."""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class ProjectFileRecord(Base):
    """Database-backed project file and metadata record."""

    __tablename__ = "project_files"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False, default="FILE")
    project: Mapped[str] = mapped_column(String(255), nullable=False, default="Unassigned", index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="Other", index=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


__all__ = ["ProjectFileRecord"]
