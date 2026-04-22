from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class DBHealthResponse(BaseModel):
    status: str
    database: str


class RedisHealthResponse(BaseModel):
    status: str
    redis: str


class WorkerHealthResponse(BaseModel):
    status: str
    workers: int


class MetricsResponse(BaseModel):
    total_companies: int
    total_users: int
    total_tasks: int
    active_tasks: int
    completed_tasks: int