from pydantic import BaseModel, EmailStr, field_validator
from app.core.enums import RoleEnum, SkillEnum
from typing import Optional
from pydantic import field_validator
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import re

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    skill: SkillEnum | None = None
    role: RoleEnum | None = None
    company_id: int | None = None

    # normalize email
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.strip().lower()

    # password validation
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")

        return value

class UserSkillUpdate(BaseModel):
    skill: SkillEnum

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[str] = None
    company_id: int
    company_name: str | None = None
    skill: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):  
    data: List[UserResponse]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.strip().lower()

