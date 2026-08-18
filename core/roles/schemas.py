from pydantic import BaseModel
from typing import Optional

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
