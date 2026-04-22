from app.models.task import Task
from sqlalchemy import func
from datetime import datetime

class TaskRepository:
    @staticmethod
    def get_tasks(db, company_id: int):
        return db.query(Task).filter(Task.company_id == company_id).all()
    
    
    @staticmethod
    def create_task(db, task_data, current_user):
        from datetime import datetime

        # Handle enum safely
        skill_value = (
            task_data.skill if task_data.skill else None
        )

        # Create task
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            assigned_to=task_data.assigned_to,
            company_id=current_user.company_id,
            skill=skill_value,
            deadline_reminder_sent=task_data.deadline_reminder_sent,
            deadline=task_data.deadline # properly mapped
        )

        # DB operations
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task
    
    @staticmethod
    def get_task_by_id(db, task_id, company_id):
        return db.query(Task).filter(Task.id == task_id, Task.company_id == company_id).first()
    

    @staticmethod
    def update_task(db,task):
        db.add(task)
        db.commit()
        db.refresh(task)

    @staticmethod
    def update_task_fields(db, task, update_data: dict):
        for key, value in update_data.items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def delete_task(db, task):
        db.delete(task)
        db.commit()    



    @staticmethod
    def count_active_tasks(db, user_id):

        return (
            db.query(func.count(Task.id))
            .filter(
                Task.assigned_to == user_id,
                Task.status != "completed"
            )
            .scalar() 
        )
    #.scalar = count(*) return only first coloumn first row

    @staticmethod
    def get_overdue_tasks(db, company_id):

        return (
            db.query(Task)
            .filter(Task.company_id == company_id)
            .filter(Task.deadline < datetime.utcnow())
            .filter(Task.status.notin_(["completed", "blocked"]))
            .all()
        )
    