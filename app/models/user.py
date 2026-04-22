from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from app.core.database import Base
from app.core.enums import RoleEnum, SkillEnum
from sqlalchemy.sql import func
from datetime import datetime   

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True)

    password = Column(String, nullable=False)

    role = Column(Enum(RoleEnum, name="roleenum"))

    skill = Column(Enum(SkillEnum, name="skillenum"),  nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    company_name = Column(String, nullable=True)