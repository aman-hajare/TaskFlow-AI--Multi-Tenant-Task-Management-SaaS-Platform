import json
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.enums import RoleEnum, SkillEnum
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserResponse    
from app.core.exceptions import AppException
from app.core.redis_client import redis_client
from app.utils.logger import logger

class UserService:
    
    @staticmethod
    def get_user_profile(user):

        return{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "company_id": user.company_id,
        "role": user.role,
        "skill": user.skill
    }

    @staticmethod
    def get_users(db, current_user, role=None, skill=None, page=1, limit=10):
        if current_user.role == "super_admin":
            cache_key = f"_users_superadmin:{role}:{skill}:{page}:{limit}"
        else:
            cache_key = f"_users:admin:{current_user.company_id}:{role}:{skill}:{page}:{limit}"

        try:
            cached_users = redis_client.get(cache_key)
            if cached_users:
                return json.loads(cached_users)

        except Exception as e:
            logger.error(f"Redis cache read failed: {e}")


        if current_user.role == "super_admin":
            query = db.query(User)
        else:
            query = db.query(User).filter(
                User.company_id == current_user.company_id
            )

        if role:
            try:
                roles_enum = RoleEnum(role)
                query = query.filter(User.role == roles_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid role value"
                )
        if skill:
            try:
                skill_enum = SkillEnum(skill)
                query = query.filter(User.skill == skill_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid skill value"
                )


        total = query.count()

        users = (
            query.order_by(User.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        result = [
            UserResponse.model_validate(user).model_dump(mode="json")
            for user in users
        ]

        response = {
            "data": result,
            "total": total,
            "page": page,
            "limit": limit
        }

        try:
         redis_client.setex(cache_key, 60, json.dumps(response))

        except Exception as e:
            logger.error(f"Redis cache write failed: {e}")

        return response
    
    @staticmethod
    def delete_user(db, user_id, current_user):
        user = UserRepository.get_users_by_id(
            db,
            user_id,
            current_user.company_id
        )

        if not user:
            raise AppException(
                message="User not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )

        #  prevent self delete
        if user.id == current_user.id:
            raise AppException(
                message="You cannot delete yourself",
                error_code="SELF_DELETE_NOT_ALLOWED",
                status_code=400
            )

        current_role = RoleEnum(current_user.role)
        target_role = RoleEnum(user.role)

        #  RBAC using ENUM
        if current_role == RoleEnum.admin:

            if target_role not in [RoleEnum.employee, RoleEnum.manager]:
                raise AppException(
                    message="Admin can only delete employee or manager",
                    error_code="PERMISSION_DENIED",
                    status_code=403
                )

        elif current_role == RoleEnum.super_admin:
            pass  # full access

        else:
            raise AppException(
                message="You are not allowed to delete users",
                error_code="PERMISSION_DENIED",
                status_code=403
            )

        UserRepository.delete_user(db, user)

        logger.warning(
            f"{current_role.value} {current_user.id} deleted user {user.id}"
        )

        return {"message": "User deleted successfully"}
    

    

    #  UPDATE SKILL WITH ENUM
    @staticmethod
    def update_user_skill(db, user_id, skill: SkillEnum, current_user):

        user = UserRepository.get_users_by_id(
            db,
            user_id,
            current_user.company_id
        )

        if not user:
            raise AppException(
                message="User not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )

        current_role = RoleEnum(current_user.role)

        if current_role not in [RoleEnum.admin, RoleEnum.manager]:
            raise AppException(
                message="Only admin or manager can update skill",
                error_code="PERMISSION_DENIED",
                status_code=403
            )

        #  assign enum value
        user.skill = skill.value

        updated_user = UserRepository.update_user(db, user)

        logger.info(
            f"{current_role.value} {current_user.id} updated skill of user {user.id} → {skill.value}"
        )

        return {
            "id": updated_user.id,
            "skill": skill.value
        }