from app.background.celery_app import celery_app
from app.core.database import SessionLocal
from app.websocket.manager import manager
from sqlalchemy import func, text
import asyncio

from contextlib import contextmanager
from datetime import datetime, timedelta

from app.models.task import Task
from app.models.user import User
from app.models.company import Company
from app.models.activity_log import ActivityLog
from app.models.notification import Notification

from app.core.redis_client import redis_client

from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.utils.email_templates import task_assigned_template
from app.utils.logger import logger

from app.ai.risk_prediction_service import RiskPredictionService
from app.repositories.task_repository import TaskRepository
from app.ai.overdue_analyzer_service import OverdueAnalyzerService

from app.repositories.task_repository import TaskRepository

# Database Context Manager
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Email task
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="app.background.tasks.send_task_assignment_email",
)
def send_task_assignment_email(self, user_email, user_name, task_title):

    try:
        body = task_assigned_template(user_name, task_title)

        EmailService.send_email(
            to_email=user_email,
            subject="New Task Assigned",
            body=body
        )

        logger.info(f"Task assignment email sent to {user_email}")

    except Exception as e:
        logger.exception("Email sending failed")
        raise self.retry(exc=e)


# Notification task
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="app.background.tasks.create_task_assignment_notification",
)
def create_task_assignment_notification(self, user_id, task_id, company_id):

    try:
        with get_db() as db:

            service = NotificationService()

            service.create_notification(
                db=db,
                user_id=user_id,
                company_id=company_id,
                title="New Task Assigned",
                message=f"You have been assigned task #{task_id}",
                event_type="TASK_ASSIGNMENT"
            )

        logger.info(f"Notification created for user {user_id}")

    except Exception as e:
        logger.exception("Notification task failed")
        raise self.retry(exc=e)



# Task 1 Deadline Reminder (notify user when task deadline is near 10 minut)
@celery_app.task(name="app.background.tasks.check_task_deadlines")
def check_task_deadlines():

    with get_db() as db:

        upcoming_deadline = datetime.utcnow() + timedelta(minutes=10)

        tasks = db.query(Task).filter(
            Task.deadline <= upcoming_deadline,
            Task.status != "completed",  
            Task.deadline_reminder_sent == False
        ).all()
        # notin_() == != (,and) !=, (Task.status != "completed" and Task.status != "blocked")

        for task in tasks:

            logger.info(f"Reminder: Task {task.id} deadline approaching")

            service = NotificationService()

            service.create_notification(
                db=db,
                user_id=task.assigned_to,
                company_id=task.company_id,
                title="Task Deadline Reminder",
                message=f"Task #{task.id} deadline is approaching"
            )

            task.deadline_reminder_sent = True

        db.commit()



# Task 2 Daily Report (Generate daily system statistics)
@celery_app.task(name="app.background.tasks.generate_daily_report")
def generate_daily_report():

    with get_db() as db:

        total_tasks = db.query(Task).count()

        completed = db.query(Task).filter(
            Task.status == "completed"
        ).count()

        logger.info(f"Daily Report: {completed}/{total_tasks} tasks completed")


# Task 3 Weekly Summary (Notify users when task deadline is near)
@celery_app.task(name="app.background.tasks.generate_weekly_summary")
def generate_weekly_summary():

    with get_db() as db:

        for user in db.query(User).yield_per(100):

            logger.info(f"Send weekly summary to user {user.id}")

            service = NotificationService()

            service.create_notification(
                db=db,
                user_id=user.id,
                company_id=None,
                title="Weekly Summary",
                message="Here is your weekly task summary"
            )

# Task 4 Clean Activity Logs (Prevent database from growing too large)
@celery_app.task(name="app.background.tasks.cleanup_old_activity_logs")
def cleanup_old_activity_logs():

    with get_db() as db:

        cutoff = datetime.utcnow() - timedelta(days=90)

        db.query(ActivityLog).filter(
            ActivityLog.timestamp < cutoff
        ).delete(synchronize_session=False)

        db.commit()

        logger.info("Old activity logs deleted")


# Task 5 Clean Notification (Delelte old notification)
@celery_app.task(name="app.background.tasks.cleanup_old_notifications")
def cleanup_old_notifications():

    with get_db() as db:

        cutoff = datetime.utcnow() - timedelta(days=30)

        db.query(Notification).filter(
            Notification.created_at < cutoff
        ).delete(synchronize_session=False)

        db.commit()

        logger.info("Old notifications deleted")




# Task 6 Rebuild analytics Cache(precompute analytics for dashboards in redis cache)
@celery_app.task(name="app.background.tasks.rebuild_analytics_cache")
def rebuild_analytics_cache():

    with get_db() as db:

        
        results = db.query(
            Task.company_id,
            func.count(Task.id)
        ).group_by(Task.company_id).all()

        for company_id, total_tasks in results:

            redis_client.setex(
                f"company:{company_id}:task_count", # Set
                3600, # Cache expires after 1 hour(3600 seconds). #ex=expire
                total_tasks
            )
        logger.info("Analytics cache rebuilt")
       
#7 Task Risk Analysis
@celery_app.task(name="app.background.tasks.analyze_task_risks")
def analyze_task_risks():

    with get_db() as db:

        tasks = db.query(Task).filter(
           Task.status != "completed", 
        ).all()


        for task in tasks:

            try:

                risk = asyncio.run(
                    RiskPredictionService.predict_task_risk(db, task)
                )

                if risk["risk_level"] in ["high", "urgent"]:

                    logger.warning(
                        f"⚠ HIGH RISK TASK {task.id}: {risk['reason']}"
                    )

                    service = NotificationService()

                    service.create_notification(
                        db=db,
                        user_id=task.assigned_to,
                        company_id=task.company_id,
                        title="High Risk Task Alert",
                        message=f"Task #{task.id} may miss its deadline: {risk['reason']}"
                    )

            except Exception as e:

                logger.error(f"Risk analysis failed for task {task.id}: {e}")

# 8 ai overdue analyzer
@celery_app.task(name="app.background.tasks.run_overdue_analysis")
def run_overdue_analysis():
    asyncio.run(_run_overdue_analysis())


async def _run_overdue_analysis():
    with get_db() as db:
        companies = db.query(Company.id).all()

        BATCH_SIZE = 5

        for i in range(0, len(companies), BATCH_SIZE):
            batch = companies[i:i + BATCH_SIZE]

            tasks = [
                OverdueAnalyzerService.analyze_overdue_tasks(db, c.id)
                for c in batch
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                logger.info(f"AI Overdue Insight: {result}")
            
            await asyncio.sleep(2)


# 2.ai risk pridictior
def analyze_task_risks():

    with get_db() as db:
        tasks = TaskRepository.count_active_tasks(db)

        for task in tasks:
            risk = asyncio.run(
                RiskPredictionService.predict_task_risk(db, task)
            )

            if risk["risk_level"] in ["high", "urgent"]:

                logger.warning(
                    f" Warning ⚠ Task {task.id} HIGH RISK: {risk['reason']}"
                )

