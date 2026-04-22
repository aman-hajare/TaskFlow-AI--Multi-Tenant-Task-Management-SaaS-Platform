from app.models.notification import Notification

class NotificationRepository:
    def create_notification(db, data):

        notification = Notification(**data)

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification
        
    @staticmethod
    def get_notifications_by_user(db, user_id, company_id):



        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.company_id == company_id   # imp
        ).order_by(Notification.created_at.desc()).all()


    @staticmethod
    def get_by_id(db, notification_id, user_id, company_id):

        return db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.company_id == company_id   # imp
        ).first()
    
    @staticmethod
    def get_by_company(db, company_id):

        return db.query(Notification).filter(
            Notification.company_id == company_id
        ).order_by(Notification.created_at.desc()).all()