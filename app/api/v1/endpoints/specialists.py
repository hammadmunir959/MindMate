from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.schemas.specialist import SpecialistCreate, SpecialistUpdate, SpecialistDetailResponse, SpecialistListResponse
from app.services.specialist_service import SpecialistService
from app.api.v1.deps import get_current_specialist, get_current_user_payload
from app.models.enums import USERTYPE

router = APIRouter()

@router.post("/", response_model=SpecialistDetailResponse, status_code=status.HTTP_201_CREATED)
def create_specialist(
    specialist_in: SpecialistCreate,
    db: Session = Depends(get_db)
):
    """Register a new specialist (Public - Registration)."""
    if SpecialistService.get_by_email(db, email=specialist_in.email):
        raise HTTPException(
            status_code=400,
            detail="The specialist with this email already exists in the system.",
        )
    return SpecialistService.create(db, data=specialist_in)


@router.get("/", response_model=List[SpecialistListResponse])
def read_specialists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Browse the specialist directory (Public).
    Returns minimal public cards — no contact details.
    """
    return SpecialistService.list(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=SpecialistDetailResponse)
def read_specialist(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_payload)
):
    """
    Get full specialist profile.
    Only accessible to the specialist themselves or an admin.
    """
    user_type = current_user.get("user_type")
    user_id = current_user.get("user_id")

    # Allow only the specialist themselves or admins
    if user_type == USERTYPE.SPECIALIST.value and str(user_id) != str(id):
        raise HTTPException(status_code=403, detail="Not authorized to view this specialist's profile.")
    if user_type == USERTYPE.PATIENT.value:
        raise HTTPException(status_code=403, detail="Patients cannot access detailed specialist profiles.")

    specialist = SpecialistService.get(db, id=id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    return specialist


@router.patch("/{id}", response_model=SpecialistDetailResponse)
def update_specialist(
    id: UUID,
    specialist_in: SpecialistUpdate,
    db: Session = Depends(get_db),
    current_specialist = Depends(get_current_specialist)
):
    """Update a specialist's profile. Requires auth and ownership."""
    if current_specialist.id != id:
        raise HTTPException(status_code=403, detail="Not enough permissions to update this profile")

    specialist = SpecialistService.get(db, id=id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    return SpecialistService.update(db, db_obj=specialist, update_data=specialist_in)


@router.delete("/{id}", response_model=SpecialistDetailResponse)
def delete_specialist(
    id: UUID,
    db: Session = Depends(get_db),
    current_specialist = Depends(get_current_specialist)
):
    """Soft delete a specialist profile. Requires auth and ownership."""
    if current_specialist.id != id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this profile")

    specialist = SpecialistService.get(db, id=id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    return SpecialistService.delete(db, db_obj=specialist)
