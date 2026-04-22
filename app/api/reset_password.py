from fastapi import APIRouter, Depends, HTTPException, Request, Query
from app.core.dependencies import require_role
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password
from app.core.rate_limiter import limiter
from app.models.user import User
from app.models.reset_pass import PasswordResetToken
from app.services.reset_pass_service import generate_otp, get_expiry
from datetime import datetime 

router = APIRouter(prefix="/password", tags=["Password Reset"])


@router.post("/forgot", summary="Request password reset",
             description="Request a password reset for the user")
@limiter.limit("5/6minute")
def forgot_password(request: Request, email: str, company_id: str, db: Session = Depends(get_db)):

    email = email.strip().lower()
    user = db.query(User).filter(
        User.email == email,
        User.company_id == company_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid email or company ID")

    otp = generate_otp()

    reset_entry = PasswordResetToken(
        user_id=user.id,
        otp=otp,
        expires_at=get_expiry(),
        is_used=False
    )

    db.add(reset_entry)
    db.commit()

    return {"message": "Request sent to admin"}


@router.post("/reset", summary="Reset password",
             description="Reset the password for the user")
@limiter.limit("5/6minute")
def reset_password(request: Request, email: str, otp: str, new_password: str, db: Session = Depends(get_db)):

    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = db.query(PasswordResetToken).filter(
        PasswordResetToken.otp == otp,
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if record.expires_at < datetime.utcnow() or  record.is_used:
        raise HTTPException(status_code=400, detail="OTP expired or already used")

    user = db.query(User).filter(User.id == record.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(new_password)

    record.is_used = True   
    db.commit()

    db.delete(record)
    db.commit()

    return {"message": "Password reset successful"}


@router.get("/otps", summary="Get active OTPs",
            description="Fetch all active password reset OTPs")
def get_otps(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin","admin"]))
):

    skip = (page - 1) * limit

    base_query = db.query(PasswordResetToken, User).join(
        User, PasswordResetToken.user_id == User.id
    ).filter(PasswordResetToken.is_used == False).order_by(PasswordResetToken.id.desc())

    # role-based filtering
    if current_user.role == "admin":
        base_query = base_query.filter(
            User.company_id == current_user.company_id
        )

    # total count (for frontend pagination)
    total = base_query.count()

    # apply pagination
    tokens = base_query.offset(skip).limit(limit).all()

    data = [
        {
            "otp": t.PasswordResetToken.otp,
            "email": t.User.email,
            "name": t.User.name,
            "expires_at": t.PasswordResetToken.expires_at
        }
        for t in tokens
    ]

    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit
    }