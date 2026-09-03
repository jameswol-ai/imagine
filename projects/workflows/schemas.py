from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkflowCreate(BaseModel):
    project_id: UUID
    step: str = Field(min_length=1, max_length=100)
    assigned_to: Optional[int] = Field(default=None, ge=1)


class WorkflowUpdate(BaseModel):
    step: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[str] = Field(default=None, min_length=1, max_length=50)
    assigned_to: Optional[int] = Field(default=None, ge=1)


class WorkflowOut(BaseModel):
    id: int
    project_id: UUID
    step: str
    status: str
    assigned_to: Optional[int]

    model_config = ConfigDict(from_attributes=True)
