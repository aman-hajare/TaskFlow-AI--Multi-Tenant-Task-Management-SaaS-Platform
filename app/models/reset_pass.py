from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.core.database import Base

class PasswordResetToken(Base):
    __tablename__ = "reset_password"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    
    otp = Column(String, nullable=True) 

    expires_at = Column(DateTime)

    is_used = Column(Boolean, default=False)