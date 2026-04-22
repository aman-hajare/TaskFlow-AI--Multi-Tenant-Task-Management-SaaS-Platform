from app.events.event_bus import event_bus
from app.events.events import TASK_ASSIGNED
from app.background.tasks import (
    send_task_assignment_email,
    create_task_assignment_notification
)
from app.repositories.user_repository import UserRepository
from app.core.database import SessionLocal
from app.utils.logger import logger


async def handle_task_assigned(data):

    logger.info(f"EVENT DATA RECEIVED: {data}")

    db = SessionLocal()


    try:

        user_id = data.get("assigned_to")
        task_id = data.get("task_id")
        company_id = data.get("company_id")
        task_title = data.get("task_title", f"Task #{task_id}")

        user = UserRepository.get_users_by_id(db, user_id,company_id)

        

        if not user:
            logger.error(f"User {user_id} not found for task assignment")
            return

        # send email
        send_task_assignment_email.delay(
            user.email,
            user.name,
            task_title
        )

        # send notification
        create_task_assignment_notification.delay(
            user_id,
            task_id,
            company_id
        )

        logger.info(
            f"TASK_ASSIGNED event handled for task {task_id}"
        )

    finally:
        db.close()


event_bus.subscribe(TASK_ASSIGNED, handle_task_assigned)