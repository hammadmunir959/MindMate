"""
Unified Authentication API
==========================
Streamlined authentication using the unified User model.
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models_new import User, UserType
from app.db.repositories_new import user_repo

router = APIRouter(prefix="/auth")

@router.post("/login/access-token", response_model=dict)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # 1. Authenticate User
    user = user_repo.GetByEmail(db, email=form_data.username)
    
    if not user:
        # Avoid timing attacks
        verify_password("dummy", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    # 2. Generate Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "type": user.user_type.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user.user_type.value
    }

@router.post("/register", response_model=dict)
def register(
    *,
    db: Session = Depends(get_db),
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    user_type: str,
) -> Any:
    """
    Register a new user (Patient or Specialist).
    """
    # 1. Check existing user
    if user_repo.GetByEmail(db, email=email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )
    
    # 2. Validate user type
    try:
        user_type_enum = UserType(user_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user type. Must be one of: {[t.value for t in UserType]}"
        )
        
    # 3. Create User and Profile Transactionally
    from app.core.security import get_password_hash
    from app.models_new import Patient, Specialist
    
    try:
        # Create User
        db_user = User(
            email=email,
            password_hash=get_password_hash(password),
            user_type=user_type_enum,
            is_active=True,
            is_locked=False
        )
        db.add(db_user)
        db.flush() # Get ID
        
        # Create Profile
        if user_type_enum == UserType.PATIENT:
            profile = Patient(
                user_id=db_user.id,
                first_name=first_name,
                last_name=last_name,
                # email is in User model
            )
            db.add(profile)
            db.flush()
            db_user.profile_id = profile.id
            
        elif user_type_enum == UserType.SPECIALIST:
            from app.models_new import SpecialistType
            profile = Specialist(
                user_id=db_user.id,
                first_name=first_name,
                last_name=last_name,
                # email is in User model
                specialist_type=SpecialistType.CLINICAL_PSYCHOLOGIST
            )
            db.add(profile)
            db.flush()
            db_user.profile_id = profile.id
            
        elif user_type_enum == UserType.ADMIN:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin registration checks not implemented here"
            )
            
        db.commit()
        db.refresh(db_user)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
        
    # 4. Return Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id), "type": db_user.user_type.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": db_user.user_type.value,
        "user_id": str(db_user.id)
    }

@router.post("/test-token", response_model=dict)
def test_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Test access token
    """
    return {
        "email": current_user.email,
        "id": str(current_user.id),
        "type": current_user.user_type.value,
        "is_active": current_user.is_active,
        "patient_id": str(current_user.patient.id) if current_user.patient else None,
        "specialist_id": str(current_user.specialist.id) if current_user.specialist else None
    }
