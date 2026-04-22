from app.models.audit_log import AuditLog


class AuditLogRepository:

    @staticmethod
    def create_audit_log(db, log_data):

        audit_log = AuditLog(**log_data)

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log