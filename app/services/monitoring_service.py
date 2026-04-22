from app.core.database import SessionLocal
from app.models.user import User
from app.models.task import Task
from app.models.company import Company
from app.core.enums import RoleEnum
from app.core.redis_client import redis_client
from app.background.celery_app import celery_app
from app.core.exceptions import AppException

from sqlalchemy import text


class MonitoringService:

    @staticmethod
    def get_queue_metrics(current_user):

        inspect = celery_app.control.inspect()

        active = inspect.active() or {}
        reserved = inspect.reserved() or {}
        scheduled = inspect.scheduled() or {}
        stats = inspect.stats() or {}

        workers = len(stats)

        active_tasks = sum(len(v) for v in active.values())
        queued_tasks = sum(len(v) for v in reserved.values())
        scheduled_tasks = sum(len(v) for v in scheduled.values())

        # worker health
        worker_status = "healthy" if stats else "down"

        # redis-based metrics
        failed_tasks = int(redis_client.get("celery_failed_tasks") or 0)
        processed_tasks = int(redis_client.get("celery_processed_tasks") or 0)

        # queue length
        try:
            queue_length = redis_client.llen("celery")
        except:
            queue_length = 0

        # active task details
        active_task_details = [
            {
                "task_name": t.get("name"),
                "task_id": t.get("id")
            }
            for worker in active.values()
            for t in worker
        ]

        return {
            "workers": workers,
            "worker_status": worker_status,
            "active_tasks": active_tasks,
            "queued_tasks": queued_tasks,
            "scheduled_tasks": scheduled_tasks,
            "queue_length": queue_length,
            "processed_tasks": processed_tasks,
            "failed_tasks": failed_tasks,
            "active_task_details": active_task_details
        }

    @staticmethod
    def check_db(current_user):

        db = SessionLocal()

        try:
            db.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}
        except Exception:
            return {"status": "error", "database": "disconnected"}
        finally:
            db.close()

    @staticmethod
    def check_redis(current_user):

        try:
            redis_client.ping()
            return {"status": "ok", "redis": "connected"}
        except Exception:
            return {"status": "error", "redis": "disconnected"}

    @staticmethod
    def check_workers(current_user):

        inspect = celery_app.control.inspect()

        active = inspect.active() or {}

        workers = len(active)

        return {
            "status": "ok" if workers > 0 else "warning",
            "workers": workers
        }

    @staticmethod
    def get_metrics(current_user):

        db = SessionLocal()

        try:

            total_companies = db.query(Company).count()

            total_users = db.query(User).count()

            total_admins = db.query(User).filter(User.role == "admin").count()

            total_managers = db.query(User).filter(User.role == "manager").count()

            total_employees = db.query(User).filter(User.role == "employee").count()

            total_tasks = db.query(Task).count()

            total_pending_tasks = db.query(Task).filter(Task.status == "pending").count()
            total_in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
            total_completed_tasks = db.query(Task).filter(Task.status == "completed").count()


            return {

                "data":{
                    "total_companies": total_companies,
                    "total_users": total_users,
                    "total_admins": total_admins,
                    "total_managers": total_managers,
                    "total_employees": total_employees,
                },

                "tasks":{
                    "total_tasks": total_tasks,
                    "pending_tasks": total_pending_tasks,
                    "in_progress_tasks": total_in_progress_tasks,
                    "completed_tasks": total_completed_tasks
                }

            }

        finally:
            db.close()


class AdminService:

    @staticmethod
    def get_admin_metrics(db, current_user):

        if current_user.role != RoleEnum.admin.value:
            raise AppException(
                message="Not authorized",
                error_code="PERMISSION_DENIED",
                status_code=403
            )

        company_id = current_user.company_id

        # USERS (ONLY SAME COMPANY)
        total_users = db.query(User).filter(
            User.company_id == company_id
        ).count()

        total_admins = db.query(User).filter(
            User.company_id == company_id,
            User.role == RoleEnum.admin.value
        ).count()

        total_managers = db.query(User).filter(
            User.company_id == company_id,
            User.role == RoleEnum.manager.value
        ).count()

        total_employees = db.query(User).filter(
            User.company_id == company_id,
            User.role == RoleEnum.employee.value
        ).count()

        #  TASKS (ONLY SAME COMPANY)
        total_tasks = db.query(Task).filter(
            Task.company_id == company_id
        ).count()

        active_tasks = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status != "completed"
        ).count()

        completed_tasks = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status == "completed"
        ).count()

        pending_tasks = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status == "pending"
        ).count()

        progress_tasks = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status == "in_progress"
        ).count()

        blocked_tasks = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status == "blocked"
        ).count()

        return {
            "users": {
                "total_users": total_users,
                "admins": total_admins,
                "managers": total_managers,
                "employees": total_employees
            },
            "tasks": {
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": progress_tasks,
                "completed_tasks": completed_tasks,
                "blocked_tasks": blocked_tasks
            }
        }