from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskStatusUpdate, TaskListResponse
from app.core.dependencies import require_role,get_current_user
from app.models.user import User
from app.core.enums import StatusEnum,PriorityEnum
from app.services.task_service import TaskService, TaskRepository

from app.core.rate_limiter import limiter


from typing import List

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/",
             response_model=TaskResponse,
             summary="Create new task",
             description="Create a new task with AI skill detection")
@limiter.limit("20/minute")
def create_task(
    request: Request,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin","manager"]))
):
    
    return TaskService.create_task(db, task, current_user)



@router.get("/",
            response_model=TaskListResponse,
            summary="Get tasks",
            description="Fetch paginated task list")
@limiter.limit("30/minute")
def get_tasks(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin","admin","manager","employee"])),
    page: int = Query(1, ge=1), # ge = greater than or equal to (default value 1 or more than 1, not 0 or -3,2..pages)
    limit: int = Query(10, le=100), #le = less than or equal to (default limit 10 and than 100 ,not 150,122,34378,... tasks
    my_tasks: bool = Query(False),
    status: StatusEnum | None = None,
    priority: PriorityEnum | None = None,
    search: str | None = None,
):

    return TaskService.get_tasks(
        db=db,
        current_user=current_user,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        search=search,
        my_tasks=my_tasks
    )


@router.get(
    "/{task_id}", 
    response_model=TaskResponse,
    summary="Get task by ID",
    description="Fetch a single task using task ID"
)
@limiter.limit("30/minute")
def get_task_by_id(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin","manager","employee"]))
):

    return TaskService.get_task_by_id(
        db=db,
        task_id=task_id,
        current_user=current_user
    )


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    task_data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin","manager","employee"]))
):
   
   return TaskService.update_task(db, task_id, task_data, current_user)

from app.schemas.task_schema import TaskUpdate

@router.patch("/{task_id}/full-update", response_model=TaskResponse)
def update_task_full(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin","manager","employee"]))
):
    return TaskService.update_task_full(
        db,
        task_id,
        task_data,
        current_user
    )

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin","manager"]))
):
    
    return TaskService.delete_task(db,task_id,current_user)

