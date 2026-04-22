from app.repositories.task_repository import TaskRepository
from app.models.task import Task

from app.core.redis_client import redis_client

from app.utils.logger import logger

import json


from app.core.exceptions import AppException

from app.logs.activity_log_service import ActivityLogService
from app.logs.audit_log_service import AuditLogService

from app.events.event_bus import event_bus
from app.events.events import TASK_CREATED, TASK_ASSIGNED

from app.ai.workload_service import WorkloadService
from app.ai.skill_detection_service import AISkillDetectionService

from app.schemas.task_schema import TaskResponse

from app.core.enums import RoleEnum

from app.repositories.user_repository import UserRepository

import asyncio

class TaskService:

    @staticmethod
    def create_task(db, task_data, current_user):

        if task_data.assigned_to:

            assigned_user = UserRepository.get_user_by_id(db, task_data.assigned_to)

            
            if not assigned_user or assigned_user.company_id != current_user.company_id:
                raise AppException(
                    message="Cannot asssign task outside your company",
                    error_code="INVAILD_ASSIGNMENT",
                    status_code=400
                )
            
            if assigned_user.role.value != "employee":
                raise AppException(
                    message="Tasks can only be assigned to employees",
                    error_code="INVALID_ASSIGNEE",
                    status_code=400
                )

        # AI skill detection
        if not getattr(task_data, "skill", None):
            logger.info(" Running AI Skill Detection...")

            try:
                ai_result = asyncio.run(
                    AISkillDetectionService.detect_skill(
                        task_data.description or task_data.title
                    )
                )
                logger.info(f" AI RESULT: {ai_result}")

                task_data.skill = ai_result["skill"]
                print("Detected skill:", task_data.skill)

                if not task_data.priority:
                    task_data.priority = ai_result["priority"]

                print("Detected priority:", task_data.priority)         

            except Exception as e:
                logger.error(f"AI skill detection failed: {e}")

        if not task_data.assigned_to and task_data.skill:
            logger.info(f" Running Smart Assignment for skill: {task_data.skill}")

            try:

                user = WorkloadService.smart_assign_user(
                    db=db,
                    company_id=current_user.company_id,
                    skill=task_data.skill
                )

                # logger.info(f" ASSIGNED USER: {user}")

                if user:
                    task_data.assigned_to = user.id        

            except Exception as e:
                logger.error(f"Smart assignment failed: {e}")

        task = TaskRepository.create_task(db, task_data, current_user)

        # publish task created event
        try:
            asyncio.run(
                event_bus.publish(
                    TASK_CREATED,
                    {
                        "task_id": task.id,
                        "created_by": current_user.id,
                        "company_id": current_user.company_id,
                    }
                )
            )
        except Exception as e:
            logger.error(f"TASK_CREATED event failed: {e}")

        # publish task assigned event
        if task.assigned_to:
            try:
                asyncio.run(
                    event_bus.publish(
                        TASK_ASSIGNED,
                        {
                            "task_id": task.id,
                            "task_title": task.title,
                            "assigned_to": task.assigned_to,
                            "company_id": current_user.company_id
                        }
                    )
                )
            except Exception as e:
                logger.error(f"TASK_ASSIGNED event failed: {e}")


        # activity log
        try:
            ActivityLogService.log_activity(
                db=db,
                user_id=current_user.id,
                company_id=current_user.company_id,
                action="CREATE_TASK",
                entity_type="TASK",
                entity_id=task.id
            )
        except Exception as e:
            logger.error(f"Activity log failed: {e}")

        # clear redis cache
        try:
            for key in redis_client.scan_iter(f"tasks_company_{current_user.company_id}*"):
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis cache clear failed: {e}")

        logger.info(
            f"User {current_user.id} created task {task.id}"
        )

        return task

    

    @staticmethod
    def get_tasks(db, current_user, page, limit, status, priority, search, my_tasks):
        if current_user.role == "super_admin":
            cache_key = f"_tasks_superadmin:{page}:{limit}:{status}:{priority}:{search}"
        else:
            cache_key = f"tasks_company_{current_user.company_id}:{page}:{limit}:{status}:{priority}:{search}:{my_tasks}"

        # 1. TRY CACHE
        try:
            cached_tasks = redis_client.get(cache_key)
            if cached_tasks:
                return json.loads(cached_tasks)
        except Exception as e:
            logger.error(f"Redis cache read failed: {e}")

        # 2. db QUERY

        if current_user.role == "super_admin":
            query = db.query(Task)
        else:    
            query = db.query(Task).filter(
                Task.company_id == current_user.company_id
            )

        if my_tasks:
            query = query.filter(Task.assigned_to == current_user.id)

        # 3. FILTERING
        if status:
            query = query.filter(Task.status == status)

        if priority:
            query = query.filter(Task.priority == priority)

        # 4. SEARCH
        if search:
            query = query.filter(Task.description.ilike(f"%{search}%"))

        # total count
        total = query.count()

        # order by
        query = query.order_by(Task.created_at.desc())

        # 5. PAGINATION
        tasks = query.offset((page - 1) * limit).limit(limit).all()
        # page-1 * limit = 0 * limit =page 0 cause database indexing start with 0 and we start with 1

        # SERIALIZATION (Full data no field loss)
        result = [
            TaskResponse.model_validate(task).model_dump(mode="json")
            for task in tasks
        ]

        response = {
            "data": result,
            "total": total,
            "page": page,
            "limit": limit
        }

        #  CACHE STORE (Json safe)
        try:
         redis_client.setex(cache_key, 60, json.dumps(response))

        except Exception as e:
          logger.error(f"Redis cache write failed: {e}")

        # RETURN Pydantic objects (FastAPI friendly)
        return response
    

    @staticmethod
    def get_task_by_id(db, task_id, current_user):

        cache_key = f"task_{task_id}_company_{current_user.company_id}"

        # check redis cache
        try:
            cached_task = redis_client.get(cache_key)

            if cached_task:
                return json.loads(cached_task)

        except Exception as e:
            logger.error(f"Redis cache read failed: {e}")

        # fetch task from repository
        task = TaskRepository.get_task_by_id(
            db=db,
            task_id=task_id,
            company_id=current_user.company_id
        )

        if not task:
            raise AppException(
                message="Task not found",
                error_code="TASK_NOT_FOUND",
                status_code=404
            )

        # serialize task
        result = TaskResponse.model_validate(task).model_dump(mode="json")


        # cache task for 60 seconds
        try:
            redis_client.setex(cache_key, 60, json.dumps(result))

        except Exception as e:
            logger.error(f"Redis cache write failed: {e}")

        return result
    

    @staticmethod 
    def update_task(db, task_id, task_data, current_user):

        task = TaskRepository.get_task_by_id(db,task_id, current_user.company_id)

        if not task:
         raise AppException(
             message="Task not found",
             error_code="TASK_NOT_FOUND",
             status_code=404
         )

        if current_user.role == "employee":
            if task.assigned_to != current_user.id:
                raise AppException(
                    message="You can only update your own tasks",
                    error_code="FORBIDDEN_ACTION",
                    status_code=403
                )

        
        # save old value BEFORE update
        old_status = task.status
        
        # update status
        task.status = task_data.status.value

        TaskRepository.update_task(db, task)

        # activity log
        ActivityLogService.log_activity(
            db=db,
            user_id=current_user.id,
            company_id=current_user.company_id,
            action="UPDATE_TASK",
            entity_type="TASK",
            entity_id=task.id
        )

        # audit log
        AuditLogService.log_change(
        db=db,
        user_id=current_user.id,
        company_id=current_user.company_id,
        entity_type="TASK",
        entity_id=task.id,
        field_name="status",
        old_value=old_status,
        new_value=task.status
    )

        # clear redis list cache
        for key in redis_client.scan_iter(f"tasks_company_{current_user.company_id}*"):
            redis_client.delete(key)

        # clear single task cache
        redis_client.delete(
            f"task_{task_id}_company_{current_user.company_id}"
        )            

        logger.info(
            f"User {current_user.id} updated task {task.id}"
        )

        return task
        
    @staticmethod
    def update_task_full(db, task_id, task_data, current_user):

        task = TaskRepository.get_task_by_id(
            db,
            task_id,
            current_user.company_id
        )

        if not task:
            raise AppException(
                message="Task not found",
                error_code="TASK_NOT_FOUND",
                status_code=404
            )
        
        if task.status == "completed":
            raise AppException(
                message="Completed task cannot be updated",
                error_code="TASK_LOCKED",
                status_code=400
            )

    
        if current_user.role.value not in ["admin", "manager"]:
            raise AppException(
                message="Only admin or manager can update task",
                error_code="FORBIDDEN",
                status_code=403
            )

        update_data = task_data.model_dump(exclude_unset=True)


        if "assigned_to" in update_data:
            user = UserRepository.get_user_by_id(db, update_data["assigned_to"])

            if not user or user.company_id != current_user.company_id:
                raise AppException(
                    message="Invalid user assignment",
                    error_code="INVALID_ASSIGNMENT",
                    status_code=400
                )

            if user.role.value in ["admin", "manager"]:
                raise AppException(
                    message="Cannot assign task to admin or manager",
                    error_code="INVALID_ASSIGNMENT",
                    status_code=400
                )
            
        updated_task = TaskRepository.update_task_fields(
            db,
            task,
            update_data
        )

        ActivityLogService.log_activity(
            db=db,
            user_id=current_user.id,
            company_id=current_user.company_id,
            action="UPDATE_TASK_FULL",
            entity_type="TASK",
            entity_id=task.id
        )

        for key in redis_client.scan_iter(f"tasks_company_{current_user.company_id}*"):
            redis_client.delete(key)

        redis_client.delete(f"task_{task_id}_company_{current_user.company_id}")

        return updated_task
    
    @staticmethod
    def delete_task(db, task_id, current_user):

        task = TaskRepository.get_task_by_id(db, task_id, current_user.company_id)
                
        if not task:
            raise AppException(
             message="Task not found",
             error_code="TASK_NOT_FOUND",
             status_code=404
         )
    

        TaskRepository.delete_task(db, task)

        ActivityLogService.log_activity(
            db=db,
            user_id=current_user.id,
            company_id=current_user.company_id,
            action="DELETE_TASK",
            entity_type="TASK",
            entity_id=task_id
        )


        # clear cache for this company
        for key in redis_client.scan_iter(f"tasks_company_{current_user.company_id}*"):
            redis_client.delete(key)

        # clear single task cache
        redis_client.delete(
            f"task_{task_id}_company_{current_user.company_id}"
        )

        logger.warning(
            f"User {current_user.id} deleted task {task_id}"
        )
        return {"message": "Task deleted"}
    
    