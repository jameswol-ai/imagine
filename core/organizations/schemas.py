from pydantic import BaseModel
from typing import Optional

class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
