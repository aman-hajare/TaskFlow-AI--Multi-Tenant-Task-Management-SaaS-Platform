from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.services.monitoring_service import MonitoringService
from app.models.reset_pass import PasswordResetToken
from app.utils.responses import success_response
from app.core.rate_limiter import limiter
from app.core.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/monitor", tags=["Monitoring"])


@router.get("/queues",
            summary="Celery Queue Metrics",
            description="Retrieve background worker queue statistics")
@limiter.limit("30/minute")
async def get_queue_metrics(request: Request, 
                            current_user: User = Depends(require_role(["super_admin"]))):
    try:
        metrics = MonitoringService.get_queue_metrics(current_user=current_user)

        return success_response(
            message="Queue metrics fetched successfully",
            data=metrics,
            current_user=current_user
        )
    except:
        return {"error": "Somthing gone wrong!"}
    
