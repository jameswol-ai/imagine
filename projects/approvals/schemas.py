from pydantic import BaseModel
from typing import Optional

class ApprovalCreate(BaseModel):
    project_id: int
    approver_id: int
    comment: Optional[str] = None

class ApprovalOut(BaseModel):
    id: int
    project_id: int
    approver_id: int
    status: str
    comment: Optional[str]

    class Config:
        orm_mode = True