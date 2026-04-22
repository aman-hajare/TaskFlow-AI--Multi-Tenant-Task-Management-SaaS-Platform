from app.repositories.activity_log_repository import ActivityLogRepository
from app.utils.logger import logger

class ActivityLogService:

    @staticmethod
    def log_activity(
        db,
        user_id,
        company_id,
        action,
        entity_type,
        entity_id
    ):
        
        try: 

            log_data = {
                "user_id": user_id,
                "company_id": company_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
            }

            ActivityLogRepository.create_log(db, log_data)

        except Exception as e:

            logger.error(f"Activity logging failed: {str(e)}")