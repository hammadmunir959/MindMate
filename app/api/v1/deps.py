from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.core.config import settings
from app.models.patient import Patient
from app.models.specialist import Specialist
from app.models.admin import Admin

# Defines the token URL (can be customized later as we split login routes)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """Decodes JWT and returns payload."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if user_id is None or user_type is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    return {"user_id": user_id, "user_type": user_type}

def get_current_specialist(
    payload: dict = Depends(get_current_user_payload), 
    db: Session = Depends(get_db)
) -> Specialist:
    """Returns the current specialist if valid."""
    if payload.get("user_type") != "specialist":
        raise HTTPException(status_code=403, detail="Not authorized, require specialist role.")
    
    try:
        user_id = UUID(payload.get("user_id"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format in token.")
        
    specialist = db.query(Specialist).filter(Specialist.id == user_id, Specialist.is_deleted == False).first()
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
        
    return specialist

def get_current_patient(
    payload: dict = Depends(get_current_user_payload), 
    db: Session = Depends(get_db)
) -> Patient:
    """Returns the current patient if valid."""
    if payload.get("user_type") != "patient":
        raise HTTPException(status_code=403, detail="Not authorized, require patient role.")
    
    try:
        user_id = UUID(payload.get("user_id"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format in token.")
        
    patient = db.query(Patient).filter(Patient.id == user_id, Patient.is_deleted == False).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    return patient

def get_current_admin(
    payload: dict = Depends(get_current_user_payload), 
    db: Session = Depends(get_db)
) -> Admin:
    """Returns the current admin if valid."""
    if payload.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized, require admin role.")
    
    try:
        user_id = UUID(payload.get("user_id"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format in token.")
        
    admin = db.query(Admin).filter(Admin.id == user_id, Admin.is_deleted == False).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
        
    return admin

def get_current_superadmin(
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    """Returns the current admin if they are a super admin."""
    from app.models.enums import AdminRoleEnum
    if current_admin.role != AdminRoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized, require super admin role.")
    return current_admin
