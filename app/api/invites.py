from fastapi import APIRouter, Depends,Query, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.enums import InviteStatusEnum, RoleEnum
from app.core.rate_limiter import limiter  
from app.services.invite_service import InviteService
from app.models.invite import Invite
from datetime import datetime, timedelta
import uuid
from app.logs.activity_log_service import ActivityLogService
from app.schemas.invite_schema import InviteResponse,InviteListResponse
from app.models.user import User
router = APIRouter(prefix="/invites", tags=["Invites"])


@router.post("/",
            summary="Send invite to user",
             description="Send an invite to a user to join the platform")
@limiter.limit("30/minute")
def send_invite(
    request: Request,
    email: EmailStr,
    role: str,
    company_id: int| None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["super_admin","admin", "manager"]))
):

    # role control

    if current_user.role.value == "super_admin":
        if role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Super admin can only invite admin"
            )

    elif current_user.role.value == "admin":
        if role not in ["manager", "employee"]:
            raise HTTPException(
                status_code=403,
                detail="Admin can only invite manager or employee"
            )

    elif current_user.role.value == "manager":
        if role != "employee":
            raise HTTPException(
                status_code=403,
                detail="Manager can only invite employee"
            )

    else:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    if current_user.role.value == "super_admin":
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="Super admin must provide company_id"
            )
    else:
        company_id = current_user.company_id

    invite = InviteService.create_invite(db, email, role, current_user,company_id=company_id)


    return InviteResponse.model_validate(invite)
    

@router.post("/{invite_id}/resend",
             summary="Resend invite",
             description="Resend invite to user if previous invite is expired or not accepted")
@limiter.limit("30/minute")
def resend_invite(
    request: Request,
    invite_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["super_admin","admin"]))
):

    # fetch invite
    invite = db.query(Invite).filter(Invite.id == invite_id).first()


    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    # company isolation
    if current_user.role.value != "super_admin":
        if invite.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Not allowed")

    # role check
    if current_user.role.value not in ["super_admin","admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    # do not allow resend if already accepted
    if invite.status == "pending":
        raise HTTPException(
            status_code=400,
            detail="Invite not expired, cannot resend invite"
        )

    if invite.status == "accepted":
        raise HTTPException(
            status_code=400,
            detail="User already joined, cannot resend invite"
        )

    # check if another active invite exists for same email
    existing_invite = db.query(Invite).filter(
        Invite.email == invite.email,
        Invite.company_id == current_user.company_id,
        Invite.status == "pending",
        Invite.id != invite.id
    ).first()

    if existing_invite:
        raise HTTPException(
            status_code=400,
            detail="Another active invite already exists for this email"
        )

    # regenerate token and expiry
    invite.token = str(uuid.uuid4())
    invite.status = "pending"
    invite.expires_at = datetime.utcnow() + timedelta(hours=24)

    db.commit()
    db.refresh(invite)

    # activity log
    ActivityLogService.log_activity(
        db=db,
        user_id=current_user.id,
        company_id=current_user.company_id,
        action="INVITE_RESENT",
        entity_type="INVITE",
        entity_id=invite.id
    )

    return InviteResponse.model_validate(invite)



@router.get("/", response_model=dict,
            summary="Get invites",
            description="Fetch paginated list of invites with optional status filter")
def get_invites(
    status: InviteStatusEnum| None= None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin","admin","manager"]))
):

    result = InviteService.get_invites(
        db=db,
        current_user=current_user,
        status=status,
        page=page,
        limit=limit
    )

    return {
        "data": [InviteListResponse.model_validate(i) for i in result["data"]],
        "total": result["total"],
        "page": result["page"],
        "limit": result["limit"]
    }








    