from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True
