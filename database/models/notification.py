# IMAGINE/database/models/notification.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(String(255), nullable=False)  # email or user identifier
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    send_email = Column(Boolean, default=True, nullable=False)
    send_in_app = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    creator = relationship("User", back_populates="notifications")
