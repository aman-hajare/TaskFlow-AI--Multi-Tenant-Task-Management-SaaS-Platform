from app.models.user import User
from app.models.task import Task
from sqlalchemy import func

from app.utils.logger import logger

class UserRepository:

    @staticmethod
    def create_user(db, user_data):

        new_user = User(
            name=user_data["name"],
            email=user_data["email"].strip().lower(),
            password=user_data["password"],
            role=user_data["role"],
            company_id=user_data["company_id"],
            company_name=user_data["company_name"],
            skill=user_data.get("skill") if user_data.get("skill") else None,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user   

    @staticmethod
    def get_all_users(db):
        return db.query(User).all()
    
    @staticmethod
    def get_users_by_company(db, company_id):
        return db.query(User).filter(
            User.company_id == company_id
        ).all()

    @staticmethod
    def get_user_by_email(db, email):
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db, user_id):
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    
    @staticmethod
    def get_users_by_id(db, user_id,company_id):
        return (
            db.query(User)
            .filter(User.id == user_id, User.company_id == company_id)
            .first()
        )
     
    
    @staticmethod
    def get_least_loaded_user_by_skill(db, company_id, skill):
        logger.info(f"Finding users with skill: {skill}")

        result = (
            db.query(User, func.count(Task.id).label("task_count"))
            .outerjoin(Task, Task.assigned_to == User.id)
            .filter(
                User.company_id == company_id,
                User.skill == skill,
                User.role.notin_(["admin","manager"])
            )
            .group_by(User.id)
            .order_by(func.count(Task.id).asc())
            .first()
        )
        logger.info(f"USERS FOUND: {result}")

        if result:
            return result[0]
        
        return None
    
    
    @staticmethod
    def delete_user(db, user):
        db.delete(user)
        db.commit()

    @staticmethod
    def update_user(db, user):
        db.commit()
        db.refresh(user)
        
        return user