from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ApprovalCreate(BaseModel):
    project_id: UUID
    approver_id: int
    comment: Optional[str] = None


class ApprovalOut(BaseModel):
    id: int
    project_id: UUID
    approver_id: int
    status: str
    comment: Optional[str] = None

    class Config:
        orm_mode = True