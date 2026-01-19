# app/api/deps.py

"""
Shared dependencies for API endpoints.
Uses new repository layer and unified User model.
"""

from typing import Generator, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.config import settings
from app.db.session import get_db

# New Models & Repositories
from app.models_new import User, Patient, Specialist, Admin, UserType
from app.db.repositories_new import (
    user_repo, 
    patient_repo, 
    specialist_repo
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Resolves to a unified User object.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        User object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Use repository to fetch user
    user = user_repo.get(db, id=user_id)
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
        
    return user


def get_current_patient(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Patient:
    """
    Get current authenticated patient profile.
    """
    if current_user.user_type != UserType.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as patient"
        )
    
    patient = patient_repo.get_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
        
    return patient


def get_current_specialist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Specialist:
    """
    Get current authenticated specialist profile.
    """
    if current_user.user_type != UserType.SPECIALIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as specialist"
        )
        
    specialist = specialist_repo.get_by_user_id(db, user_id=current_user.id)
    if not specialist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist profile not found"
        )
        
    return specialist


def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated admin.
    Returns the User object (as Admin profile is separate but User has permissions)
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as admin"
        )
    return current_user


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_patient",
    "get_current_specialist",
    "get_current_admin",
    "oauth2_scheme",
]
