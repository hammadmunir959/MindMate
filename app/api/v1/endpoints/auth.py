from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.patient_service import PatientService
from app.services.specialist_service import SpecialistService
from app.services.admin_service import AdminService
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Unified login for patients, specialists, and admins."""
    user = None
    hashed_password = ""
    
    if data.user_type == "patient":
        user = PatientService.get_patient_by_email(db, data.email)
        if user:
            hashed_password = user.hashed_password
    elif data.user_type == "specialist":
        user = SpecialistService.get_by_email(db, data.email)
        if user:
            # Note: Specialist model uses hashed_password too in app
            hashed_password = user.hashed_password
    elif data.user_type == "admin":
        user = AdminService.get_admin_by_email(db, data.email)
        if user:
            hashed_password = user.hashed_password
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")

    if not user or not verify_password(data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, user_type=data.user_type, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": data.user_type,
        "user_id": str(user.id)
    }
