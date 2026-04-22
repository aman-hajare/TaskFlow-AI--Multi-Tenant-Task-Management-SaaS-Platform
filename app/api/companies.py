from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.company_schema import CompanyCreate, CompanyListResponse
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.company_service import CompanyService
from app.core.enums import RoleEnum
from app.repositories.company_repository import CompanyRepository


router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/",
             summary="Create company",
             description="Create a new company")
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin"]))
):
     if current_user.role != RoleEnum.super_admin:
        raise HTTPException(
            status_code=403,
            detail="Only super admin can create company"
        )

     existing = CompanyRepository.get_company_by_name(db, data.name)

     if existing:
        raise HTTPException(
            status_code=400,
            detail="Company already exists"
        )

     return CompanyRepository.create_company(db, data.name)


@router.get("/", response_model=CompanyListResponse,
            summary="Get companies",
            description="This is taskflow AI platform where you can manage your tasks efficiently. Fetch paginated list of companies with optional filter to show only the company of the current user")
def get_companies(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    my_company: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    result = CompanyService.get_companies(db=db, page=page, limit=limit, my_company=my_company, current_user=current_user)
    return result

@router.get("/{company_id}")
def get_company(company_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)
):
    return CompanyService.get_company_by_id(db,company_id,current_user)

@router.delete("/{company_id}")
def delete_company(company_id:int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(["super_admin"]))
                  ):
    return CompanyService.delete_company(db,company_id,current_user)