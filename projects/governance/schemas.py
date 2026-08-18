from pydantic import BaseModel
from typing import Optional

class GovernanceCreate(BaseModel):
    project_id: int
    rule_name: str
    description: Optional[str] = None

class GovernanceOut(BaseModel):
    id: int
    project_id: int
    rule_name: str
    description: Optional[str]
    status: str

    class Config:
        orm_mode = True