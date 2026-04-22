from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime   

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    company_id = Column(Integer, nullable=False)

    entity_type = Column(String, nullable=False)

    entity_id = Column(Integer, nullable=False)

    field_name = Column(String, nullable=False)

    old_value = Column(String, nullable=True)

    new_value = Column(String, nullable=True)

    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)