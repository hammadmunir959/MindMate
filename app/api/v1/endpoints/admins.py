import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1 import deps
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminUpdate, AdminResponse
from app.services.admin_service import AdminService

router = APIRouter()

@router.post("/", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def create_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: AdminCreate,
    current_admin: Admin = Depends(deps.get_current_superadmin),
) -> Any:
    """Create new admin."""
    return AdminService.create_admin(db=db, admin_in=admin_in)

@router.get("/{id}", response_model=AdminResponse)
def get_admin(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_admin: Admin = Depends(deps.get_current_superadmin),
) -> Any:
    """Get admin by ID."""
    return AdminService.get_admin(db=db, admin_id=id)

@router.patch("/{id}", response_model=AdminResponse)
def update_admin(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    admin_in: AdminUpdate,
    current_admin: Admin = Depends(deps.get_current_superadmin),
) -> Any:
    """Update an admin."""
    return AdminService.update_admin(db=db, admin_id=id, admin_in=admin_in)

@router.get("/", response_model=list[AdminResponse])
def get_admins(
    db: Session = Depends(deps.get_db),
    current_admin: Admin = Depends(deps.get_current_superadmin),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve admins."""
    return AdminService.list_admins(db=db, skip=skip, limit=limit)

@router.post("/setup-superadmin", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def setup_superadmin(
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    """One-time setup for the superadmin based on env credentials."""
    return AdminService.setup_superadmin(db=db)
