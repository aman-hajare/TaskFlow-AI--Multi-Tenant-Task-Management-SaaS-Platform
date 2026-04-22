import uuid
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.repositories.invite_repository import InviteRepository
from app.repositories.company_repository import CompanyRepository
from app.core.enums import InviteStatusEnum
from app.logs.activity_log_service import ActivityLogService
from app.models.invite import Invite
from app.models.user import User


class InviteService:

    @staticmethod
    def create_invite(db, email, role, current_user, company_id=None):

        # determine company_id
        if current_user.role.value == "super_admin":
            if not company_id:
                raise HTTPException(
                    status_code=400,
                    detail="Super admin must provide company_id"
                )
            company = CompanyRepository.get_company_by_id(db, company_id)

            if not company:
                raise HTTPException(
                    status_code=400,
                    detail="Company not found"
                )

        else:
            if company_id and company_id != current_user.company_id:
                raise HTTPException(
                    status_code=400,
                    detail="Wrong company id"
                )
            company_id = current_user.company_id
        
        existing_user = db.query(User).filter(
            User.email == email,
            User.company_id == company_id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User already part of this company"
            )
                

        # check existing invite
        email = email.strip().lower() 
        existing_invite = db.query(Invite).filter(
            Invite.email == email,
            Invite.company_id == company_id,
            Invite.status.in_([
                InviteStatusEnum.pending,
                InviteStatusEnum.accepted
            ])
        ).first()

        if existing_invite:

            if existing_invite.status == InviteStatusEnum.pending:
                raise HTTPException(
                    status_code=400,
                    detail="Invite already sent to this email"
                )

            if existing_invite.status == InviteStatusEnum.accepted:
                raise HTTPException(
                    status_code=400,
                    detail="User already joined this company"
                )

        # create invite
        token = str(uuid.uuid4())

        invite_data = {
            "email": email,
            "role": role,
            "company_id": company_id,
            "invited_by": current_user.id,
            "token": token,
            "status": InviteStatusEnum.pending,
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }

        invite = InviteRepository.create_invite(db, invite_data)

        # activity log
        ActivityLogService.log_activity(
            db=db,
            user_id=current_user.id,
            company_id=company_id,
            action="INVITE_SENT",
            entity_type="INVITE",
            entity_id=invite.id
        )

        return invite

    @staticmethod
    def validate_invite(db, token):

        invite = InviteRepository.get_by_token(db, token)

        if not invite:
            raise HTTPException(status_code=404, detail="Invalid invite")

        if invite.expires_at < datetime.utcnow():
            invite.status = InviteStatusEnum.expired
            db.commit()
            db.refresh(invite)

            raise HTTPException(status_code=400, detail="Invite expired")
        
        if invite.status != InviteStatusEnum.pending:
            raise HTTPException(status_code=400, detail="Invite already used")

        return invite

    @staticmethod
    def mark_used(db, invite):

        invite.status = InviteStatusEnum.accepted
        db.commit()
        db.refresh(invite)

        # activity log
        ActivityLogService.log_activity(
            db=db,
            user_id=invite.invited_by,
            company_id=invite.company_id,
            action="INVITE_ACCEPTED",
            entity_type="INVITE",
            entity_id=invite.id
        )

        return invite

    @staticmethod
    def get_invites(db, current_user, status=None, page=1, limit=10):

        if current_user.role.value == "super_admin":
            expired_invites = db.query(Invite).filter(
                Invite.status == InviteStatusEnum.pending,
                Invite.expires_at < datetime.utcnow()
            ).all()
        else:
            expired_invites = db.query(Invite).filter(
                Invite.company_id == current_user.company_id,
                Invite.status == InviteStatusEnum.pending,
                Invite.expires_at < datetime.utcnow()
            ).all()

        for invite in expired_invites:
            invite.status = InviteStatusEnum.expired

        if expired_invites:
            db.commit()

        # super admin sees all
        if current_user.role.value == "super_admin":
            query = db.query(Invite)
        else:
            query = db.query(Invite).filter(
                Invite.company_id == current_user.company_id
            )

        # filter by status
        if status:
            try:
                status_enum = InviteStatusEnum(status)
                query = query.filter(Invite.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid status value"
                )

        total = query.count()

        invites = (
            query.order_by(Invite.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
            "data": invites,
            "total": total,
            "page": page,
            "limit": limit
        }