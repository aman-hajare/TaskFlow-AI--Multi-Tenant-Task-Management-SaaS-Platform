from fastapi import APIRouter, Depends

from app.services.monitoring_service import MonitoringService
from app.utils.responses import success_response

from app.models.user import User
from app.core.dependencies import require_role

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="Check API health")
def health(current_user: User = Depends(require_role(["super_admin"]))):

    return success_response(
        message="API is running",
        data={"status": "ok"},
        current_user=current_user
    )


@router.get("/db", summary="Check database connection")
def db_health(current_user: User = Depends(require_role(["super_admin"]))):

    result = MonitoringService.check_db(current_user)

    return success_response(
        message="Database health",
        data=result,
        current_user=current_user
    )


@router.get("/redis", summary="Check redis connection")
def redis_health(current_user: User = Depends(require_role(["super_admin"]))):

    result = MonitoringService.check_redis(current_user)

    return success_response(
        message="Redis health",
        data=result,
        current_user=current_user
    )


@router.get("/worker", summary="Check celery workers")
def worker_health(current_user: User = Depends(require_role(["super_admin"]))):

    result = MonitoringService.check_workers(current_user)

    return success_response(
        message="Worker health",
        data=result,
        current_user=current_user
    )


@router.get("/metrics", summary="System metrics")
def metrics(current_user: User = Depends(require_role(["super_admin"]))):

    result = MonitoringService.get_metrics(current_user)

    return success_response(current_user,
        message="System metrics",
        data=result
    )

# add try except and async
