from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "taskflow",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)


# Celery Beat Schedule
celery_app.conf.beat_schedule = {

    #1. celery Beat Schedule(Run job every 60 seconds)
    "check-deadlines-every-minute": {
        "task": "app.background.tasks.check_task_deadlines",
        "schedule": 60,
    },

    #2. Send daily report ,midnight (12:00 AM)
    "daily-report": {
        "task": "app.background.tasks.generate_daily_report",
        "schedule": crontab(hour=0, minute=0),
    },

    #3. Send weekly summary (Every Monday 9 AM)
    "weekly-summary": {
        "task": "app.background.tasks.generate_weekly_summary",
        "schedule": crontab(hour=9, minute=0, day_of_week="monday"),
    },

    #4. Clean old acivity logs (Every day 3 AM)
    "cleanup-logs": {
        "task": "app.background.tasks.cleanup_old_activity_logs",
        "schedule": crontab(hour=3, minute=0),
    },

    #5. Clean old notifications (Every day 4 AM)
    "cleanup-notifications": {
        "task": "app.background.tasks.cleanup_old_notifications",
        "schedule": crontab(hour=4, minute=0),
    },

    #6. Rebuild analytics cache (Every day at 2:30 AM)
    "rebuild-cache": {
        "task": "app.background.tasks.rebuild_analytics_cache",
        "schedule": crontab(hour=2, minute=30),
    },

    #7. ai risk analyzer (every 6 hours, 00:00, 06:00, 12:00, 18:00)
    "analyze-task-risks": {
        "task": "app.background.tasks.analyze_task_risks",
        "schedule": crontab(minute=0, hour='*/6'),  # every 6 hours
    },

    #8 ai overdue analyzer(every hours)
    "ai_overdue_analysis": {
        "task": "app.background.tasks.run_overdue_analysis",
        "schedule": crontab(minute=0, hour='*/6'),
    },

}

# we choose run at night cause lowest user traffic minimal system load(this is called maintenace window)

# Recommended timezone for Celery
celery_app.conf.timezone = "UTC"

# Automatically discover tasks
celery_app.autodiscover_tasks(["app.background"])