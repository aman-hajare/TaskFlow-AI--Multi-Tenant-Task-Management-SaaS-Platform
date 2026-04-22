from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime
from app.core.database import Base

from app.core.enums import InviteStatusEnum, RoleEnum

class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, nullable=False)

    role = Column(Enum(RoleEnum, name="roleenum"), nullable=False)

    company_id = Column(Integer, ForeignKey("companies.id"))

    invited_by = Column(Integer, ForeignKey("users.id"))

    token = Column(String, unique=True, nullable=False)
    
    status = Column(Enum(InviteStatusEnum, name="inviteenum"), default=InviteStatusEnum.pending)  # pending / accepted / expired

    created_at = Column(DateTime, default=datetime.utcnow)

    expires_at = Column(DateTime, nullable=False)