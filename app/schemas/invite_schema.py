from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class InviteCreate(BaseModel):
    email: EmailStr
    role: str


class InviteResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    company_id: int
    invited_by: int
    status: str
    token: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class InviteListResponse(BaseModel):
    id: int
    email: EmailStr
    token: str
    role: str
    status: str
    company_id: int
    invited_by: int
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True