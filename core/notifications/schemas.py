from pydantic import BaseModel, EmailStr
from typing import Optional

class NotificationCreate(BaseModel):
    to: EmailStr
    subject: str
    body: str
    send_email: bool = True
    send_in_app: bool = True
