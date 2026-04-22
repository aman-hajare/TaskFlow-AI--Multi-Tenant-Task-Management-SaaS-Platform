from sqlalchemy import Column, Integer, String, ForeignKey,  DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.enums import SkillEnum, StatusEnum, PriorityEnum
from datetime import datetime   

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(String)

    status = Column(Enum(StatusEnum, name="statusenum"), default=StatusEnum.pending)
    
    priority = Column(Enum(PriorityEnum, name="priorityenum"), default=PriorityEnum.medium)

    assigned_to = Column(Integer, ForeignKey("users.id"))

    company_id = Column(Integer, ForeignKey("companies.id"))

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    deadline = Column(DateTime, nullable=True)

    skill = Column(Enum(SkillEnum, name="skillenum"),  nullable=True)
    
    deadline_reminder_sent = Column(Boolean, default=False, nullable=False)