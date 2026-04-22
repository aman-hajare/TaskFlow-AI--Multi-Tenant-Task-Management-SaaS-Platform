from app.repositories.notification_repository import NotificationRepository
from app.core.exceptions import AppException
from app.models.notification import Notification
from app.utils.logger import logger
from app.websocket.manager import manager
from app.core.redis_client import redis_client
from app.core.enums import RoleEnum
import asyncio
import json


class NotificationService:

    @staticmethod
    def create_notification(db, user_id, company_id, title, message, event_type=None):

        
        if not user_id:
            return None
        
        if event_type != "TASK_ASSIGNMENT":
            return None

        data = {
            "user_id": user_id,
            "company_id": company_id,
            "title": title,
            "message": message,
        }

        # save to DB
        notification = NotificationRepository.create_notification(db, data)

        # clear cache
        try:
            pattern = f"notifications_{company_id}:{user_id}*"
            keys = list(redis_client.scan_iter(pattern))

            if keys:
                redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")

        # websocket push
        try:
            asyncio.run(
                manager.send_notification(
                    user_id=user_id,
                    company_id=company_id,
                    message={
                        "title": title,
                        "message": message
                    }
                )
            )
        except Exception as e:
            logger.error(f"WebSocket send failed: {e}")

        return notification 


    @staticmethod
    def get_notifications(db, current_user, is_read, page, limit):

        cache_key = f"notifications_{current_user.company_id}:{current_user.id}:{current_user.role.value}:{page}:{limit}:{str(is_read)}"

        # try cache
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache read failed: {e}")

        # base query
        if current_user.role == RoleEnum.admin.value or current_user.role == RoleEnum.manager.value:
            query = db.query(Notification).filter(
                Notification.company_id == current_user.company_id
            )
        else:
            query = db.query(Notification).filter(
                Notification.user_id == current_user.id,
                Notification.company_id == current_user.company_id
            )

        # filter
        if is_read is None:
            query = query.filter(Notification.is_read == False)
        else:
            query = query.filter(Notification.is_read == is_read)

        # add serch notificaion by users 

        # total
        total = query.count()

        # order + pagination
        notifications = (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        # serialize
        result = [
            {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ]

        response = {
            "data": result,
            "total": total,
            "page": page,
            "limit": limit
        }

        # cache
        try:
            redis_client.setex(cache_key, 60, json.dumps(response))
        except Exception as e:
            logger.error(f"Cache write failed: {e}")

        return response


    @staticmethod
    def mark_as_read(db, notification_id, current_user):

        # block manager
        if current_user.role.value == "manager":
            raise AppException(
                message="Managers are not allowed to mark notifications as read",
                error_code="FORBIDDEN_ACTION",
                status_code=403
            )

        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.company_id == current_user.company_id
        ).first()

        if not notification:
            raise AppException(
                message="Notification not found",
                error_code="NOTIFICATION_NOT_FOUND",
                status_code=404
            )

        notification.is_read = True
        db.commit()

        # clear cache
        try:
            pattern = f"notifications_{current_user.company_id}:{current_user.id}*"
            keys = list(redis_client.scan_iter(pattern))
            if keys:
                redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")

        return {"message": "Notification marked as read"}