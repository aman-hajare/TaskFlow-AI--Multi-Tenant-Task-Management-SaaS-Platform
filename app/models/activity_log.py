from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    company_id = Column(Integer, nullable=False)

    action = Column(String, nullable=False)

    entity_type = Column(String, nullable=False)

    entity_id = Column(Integer, nullable=False)

    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)