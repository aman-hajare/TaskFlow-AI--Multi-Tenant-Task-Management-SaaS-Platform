from pydantic import BaseModel

class TaskSummaryRequest(BaseModel):
    description: str


class PriorityRequest(BaseModel):
    title: str
    description: str




from pydantic import BaseModel


class Insight(BaseModel):
    summary: str
    risk_level: str


class Recommendation(BaseModel):
    action: str
    priority: str

class TaskInsight(BaseModel):
    task_id: int
    reason: str

class OverdueAIResponse(BaseModel):
    insight: dict
    tasks: list[TaskInsight]
    recommendation: dict