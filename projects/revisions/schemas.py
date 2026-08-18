from pydantic import BaseModel

class RevisionCreate(BaseModel):
    project_id: int
    description: str
    created_by: int

class RevisionOut(BaseModel):
    id: int
    project_id: int
    description: str
    created_by: int

    class Config:
        orm_mode = True