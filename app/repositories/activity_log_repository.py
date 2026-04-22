from app.models.activity_log import ActivityLog

class ActivityLogRepository:

    @staticmethod
    def create_log(db, log_data):

        activity = ActivityLog(**log_data)

        db.add(activity)
        db.commit()
        db.refresh(activity)

        return activity