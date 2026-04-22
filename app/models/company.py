from sqlalchemy import Column, Integer, String, DateTime,func
from app.core.database import Base
from datetime import datetime   

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
