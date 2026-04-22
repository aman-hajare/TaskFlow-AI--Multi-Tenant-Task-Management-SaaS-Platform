from app.repositories.user_repository import UserRepository

class WorkloadService:

    @staticmethod
    def smart_assign_user(db, company_id, skill):

        user = UserRepository.get_least_loaded_user_by_skill(
            db=db,
            company_id=company_id,
            skill=skill,
        )

        return user