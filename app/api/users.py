from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.task import Task
from app.core.exceptions import AppException
from app.services.user_service import UserService
from app.schemas.user_schema import UserListResponse, UserSkillUpdate
from app.repositories.user_repository import UserRepository
from app.core.rate_limiter import limiter
from app.core.enums import RoleEnum, SkillEnum
from typing import Optional

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserListResponse,
            summary="Get users",
            description="Fetch paginated list of users with optional filters for role and skill")
def get_users(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    role: RoleEnum | None = Query(None),
    skill: SkillEnum | None = Query(None)
):
    result = UserService.get_users(
        db=db,
        current_user=current_user,
        page=page,
        limit=limit,
        role=role,
        skill=skill
    )
    return result


@router.get("/me",
    summary="Get my profile",
    description="Fetch the profile of the currently authenticated user"
)
def get_me(current_user: User = Depends(get_current_user)):
    
    return UserService.get_user_profile(current_user)



@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Delete user based on role permissions"
)
@limiter.limit("10/minute")
def delete_user(
    user_id: int,
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "admin"]))
):
    tasks = db.query(Task).filter(Task.assigned_to == user_id).count()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
            raise AppException(
                message="User not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
    
    if user.id == current_user.id:
            raise AppException(
                message="You cannot delete yourself",
                error_code="SELF_DELETE_NOT_ALLOWED",
                status_code=400
            )

    if tasks > 0:
        raise AppException(
            message="User has assigned tasks. Please reassign or delete tasks first.",
            error_code="USER_HAS_TASKS",
            status_code=400
        )
    try:
        if current_user.role == "super_admin":
            user = db.query(User).filter(User.id == user_id).first()
            UserRepository.delete_user(db, user)
        else:
          user = UserService.delete_user(db=db,user_id=user_id,current_user=current_user)
    except:
            raise AppException(
                    message="User have company association, cannot delete user",
                    error_code="USER_DELETE_FAILED",
                    status_code=400
                )
    return user


# UPDATE USER SKILL ONLY
@router.patch(
    "/{user_id}/skill",
    summary="Update user skill",
    description="Only admin and manager can update user skill"
)
@limiter.limit("10/minute")
def update_user_skill(
    user_id: int,
    request: Request,
    data: UserSkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):

    return UserService.update_user_skill(
        db=db,
        user_id=user_id,
        skill=data.skill,
        current_user=current_user
    )