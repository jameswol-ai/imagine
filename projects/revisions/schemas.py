from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class RevisionCreate(BaseModel):
    project_id: UUID
    description: str
    created_by: int


class RevisionOut(BaseModel):
    id: int
    project_id: UUID
    description: str
    created_by: int

    class Config:
        orm_mode = True