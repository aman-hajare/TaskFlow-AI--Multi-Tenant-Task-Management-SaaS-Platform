from sqlalchemy import func
from app.models.company import Company

class CompanyRepository:
    
    @staticmethod
    def create_company(db, company_name):

        new_company = Company(name=company_name.strip())

        db.add(new_company)
        db.commit()
        db.refresh(new_company)

        return new_company
    
    @staticmethod
    def get_companies(db):
        return db.query(Company).all()
    
    @staticmethod
    def get_company_by_id(db, company_id):
         return db.query(Company).filter(Company.id == company_id).first()
    
    @staticmethod
    def get_companyy_by_id(db, company_id, current_user):
         return db.query(Company).filter(Company.id == company_id).first()
    
    @staticmethod
    def get_company_by_name(db, name):
        return db.query(Company).filter(func.lower(Company.name)== name.lower()).first()
    
    @staticmethod
    def delete_company(db,company):
        db.delete(company)
        db.commit()