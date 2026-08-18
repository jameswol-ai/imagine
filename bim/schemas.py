from pydantic import BaseModel
from typing import Optional

class BuildingCreate(BaseModel):
    project_id: int
    name: str
    address: Optional[str] = None

class BuildingOut(BaseModel):
    id: int
    project_id: int
    name: str
    address: Optional[str]

    class Config:
        orm_mode = True