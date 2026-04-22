from pydantic import BaseModel
from datetime import datetime
from fastapi import Query

# Base (shared fields)
class NotificationBase(BaseModel):
    title: str
    message: str


# Create schema (optional, for future use)
class NotificationCreate(NotificationBase):
    user_id: int
    company_id: int


# Response schema (MAIN)
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    title: str
    message: str
    is_read: bool | None = Query(None)
    created_at: datetime

    class Config:
        from_attributes = True


# Paginated response imp
class NotificationListResponse(BaseModel):
    data: list[NotificationResponse]
    total: int
    page: int
    limit: int