from pydantic import BaseModel
from app.core.enums import SkillEnum, StatusEnum, PriorityEnum
from datetime import  datetime

class TaskCreate(BaseModel):
    title: str
    description: str 
    priority: PriorityEnum | None = None
    skill: SkillEnum | None = None
    assigned_to: int | None = None
    deadline: datetime
    deadline_reminder_sent: bool | None = None
    
class TaskStatusUpdate(BaseModel):
    status: StatusEnum 

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: PriorityEnum | None = None
    skill: SkillEnum | None = None
    assigned_to: int | None = None
    deadline: datetime | None = None


class TaskResponse(BaseModel):
    id: int | None = None
    title: str | None = None
    company_id: int | None = None
    description: str | None = None
    assigned_to: int | None = None
    skill: SkillEnum | None = None
    priority: PriorityEnum | None = None
    status: StatusEnum | None = None
    deadline: datetime | None = None
    deadline_reminder_sent: bool | None = None
    created_at: datetime | None = None

    class Config: 
        from_attributes = True    

        
class TaskListResponse(BaseModel):
    data: list[TaskResponse]
    total: int
    page: int
    limit: int

    


# add skill in response