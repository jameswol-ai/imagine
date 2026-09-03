from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RevisionCreate(BaseModel):
    project_id: UUID
    description: str = Field(min_length=1, max_length=255)
    created_by: int = Field(ge=1)


class RevisionOut(BaseModel):
    id: int
    project_id: UUID
    description: str
    created_by: int

    model_config = ConfigDict(from_attributes=True)
