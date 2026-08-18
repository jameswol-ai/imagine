from pydantic import BaseModel

class PermissionCreate(BaseModel):
    name: str
    description: str | None = None

class PermissionOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        orm_mode = True
