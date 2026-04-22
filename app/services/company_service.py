from fastapi import HTTPException
from sqlalchemy.orm import outerjoin
from app.models.company import Company
from app.models.user import User
from app.repositories.company_repository import CompanyRepository
from app.core.exceptions import AppException

class CompanyService:

    @staticmethod
    def create_company(db, company_data,current_user):
        return CompanyRepository.create_company(db, company_data,current_user)
    

    @staticmethod
    def get_companies(db, current_user, my_company: bool, page: int = 1, limit: int = 10):

        query = db.query(Company)

        if my_company:
            query = query.filter(Company.id == current_user.company_id)

        total = query.count()

        users = (
            query.order_by(Company.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        if not users:
            raise HTTPException(status_code=404, detail="Company not found")

        return {
            "data": users,
            "total": total,
            "page": page,
            "limit": limit
        }


    
    @staticmethod
    def get_company_by_id(db, company_id, current_user):

        company = CompanyRepository.get_companyy_by_id(db, company_id, current_user)
        if not company:
            raise AppException(
             message="company not found",
             error_code="COMPANY_NOT_FOUND",
             status_code=404
         )
        
        return company
    

    
    @staticmethod
    def delete_company(db, company_id,current_user):

        company = CompanyRepository.get_companyy_by_id(db, company_id, current_user)
                
        if not company:
            raise AppException(
             message="company not found",
             error_code="COMPANY_NOT_FOUND",
             status_code=404
         )


        try:
         CompanyRepository.delete_company(db, company)
        except:
            raise AppException(
             message="First Delete Company All Users and Tasks",
             error_code="COMPANY_DELETE_FAILED",
             status_code=400
         )
        
        return {"message": "company deleted"}
    
   