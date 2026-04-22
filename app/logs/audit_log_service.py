from app.repositories.audit_log_repository import AuditLogRepository
from app.utils.logger import logger


class AuditLogService:

    @staticmethod
    def log_change(
        db,
        user_id,
        company_id,
        entity_type,
        entity_id,
        field_name,
        old_value,
        new_value
    ):

        try:

            log_data = {
                "user_id": user_id,
                "company_id": company_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "field_name": field_name,
                "old_value": str(old_value),
                "new_value": str(new_value)
            }

            AuditLogRepository.create_audit_log(db, log_data)

        except Exception as e:

            logger.error(f"Audit logging failed: {str(e)}")
