from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification_schema import NotificationListResponse
from app.core.dependencies import get_current_user, require_role
from app.models.user import User



router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin","manager","employee"])),
    is_read: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100)
):
    
    
    return NotificationService.get_notifications(db, current_user, is_read, page, limit)


@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
     current_user: User = Depends(require_role(["employee"]))
):
    
    return NotificationService.mark_as_read(
        db, notification_id, current_user
    )