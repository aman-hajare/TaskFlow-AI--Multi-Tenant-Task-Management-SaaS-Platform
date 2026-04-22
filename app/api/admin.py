from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.services.monitoring_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/metrics",
    summary="Get admin dashboard metrics",
    description="Returns company-level metrics for admin"
)
def get_admin_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["admin"]))
):

    return AdminService.get_admin_metrics(
        db=db,
        current_user=current_user
    )

