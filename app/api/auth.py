from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate
from app.services.auth_service import AuthService

from app.core.rate_limiter import limiter
from fastapi import Request

from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register",
             response_model=UserResponse,
             summary="Register a new user",
             description="Create a new user account in the system")

@limiter.limit("10/minute")
def register(request: Request, user_data: UserCreate, token: str | None = None, db: Session = Depends(get_db)):

    return AuthService.register_user(db,user_data, token)


@router.post("/login",
             summary="User login",
             description="Authenticate user and return JWT token")
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    return AuthService.login_user(db, form_data)



