from pydantic import BaseModel
from typing import Optional

class WorkflowCreate(BaseModel):
    project_id: int
    step: str
    assigned_to: Optional[int] = None

class WorkflowOut(BaseModel):
    id: int
    project_id: int
    step: str
    status: str
    assigned_to: Optional[int]

    class Config:
        orm_mode = True