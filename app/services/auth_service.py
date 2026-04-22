from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token
from app.services.invite_service import InviteService
from app.utils.logger import logger
from app.logs.activity_log_service import ActivityLogService
from typing import Optional
from app.core.enums import RoleEnum


class AuthService:

    @staticmethod
    def register_user(db, user_data, token: Optional[str] = None):

        # normalize email
        email = user_data.email.strip().lower()

        # check existing user
        existing_user = UserRepository.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # INVITE FLOW (HIGHEST PRIORITY)
        if token:
            invite = InviteService.validate_invite(db, token)

            if email != invite.email:
                raise HTTPException(
                    status_code=400,
                    detail="This invite is not for this email"
                )

            company = CompanyRepository.get_company_by_id(db, invite.company_id)

            if not company:
                raise HTTPException(status_code=404, detail="Company not found")

            user_dict = user_data.model_dump()

            user_dict["email"] = email
            user_dict["company_id"] = company.id
            user_dict["company_name"] = company.name
            user_dict["role"] = invite.role
            user_dict["password"] = hash_password(user_dict["password"])

            # role-based skill validation
            if invite.role == RoleEnum.employee and not user_data.skill:
                raise HTTPException(
                    status_code=400,
                    detail="Employee must have a skill"
                )

            new_user = UserRepository.create_user(db, user_dict)

            InviteService.mark_used(db, invite)

            ActivityLogService.log_activity(
                db=db,
                user_id=new_user.id,
                company_id=new_user.company_id,
                action="USER_REGISTERED_VIA_INVITE",
                entity_type="USER",
                entity_id=new_user.id
            )

            return new_user

        # SUPER ADMIN FLOW
        if user_data.role == RoleEnum.super_admin:

            user_dict = user_data.model_dump()

            user_dict["email"] = email
            user_dict["password"] = hash_password(user_dict["password"])
            user_dict["company_id"] = None
            user_dict["company_name"] = "TaskFlow-System"

            new_user = UserRepository.create_user(db, user_dict)

            ActivityLogService.log_activity(
                db=db,
                user_id=new_user.id,
                company_id=None,
                action="SUPER_ADMIN_REGISTERED",
                entity_type="USER",
                entity_id=new_user.id
            )

            return new_user

        # BLOCK NON-INVITE USERS
        raise HTTPException(
            status_code=400,
            detail="Registration only allowed via invite"
        )

    @staticmethod
    def login_user(db, form_data):

        user = UserRepository.get_user_by_email(db, form_data.username)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"user_id": user.id})

        ActivityLogService.log_activity(
            db=db,
            user_id=user.id,
            company_id=user.company_id,
            action="USER_LOGIN",
            entity_type="USER",
            entity_id=user.id
        )

        logger.info(f"User {user.email} logged in")

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    