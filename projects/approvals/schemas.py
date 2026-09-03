from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApprovalCreate(BaseModel):
    project_id: UUID
    approver_id: int = Field(ge=1)
    comment: Optional[str] = Field(default=None, max_length=255)


class ApprovalUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=50)
    comment: Optional[str] = Field(default=None, max_length=255)


class ApprovalOut(BaseModel):
    id: int
    project_id: UUID
    approver_id: int
    status: str
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
