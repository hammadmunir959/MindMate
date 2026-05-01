from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentListResponse
from app.services.appointment import AppointmentService
from app.api.v1.deps import get_current_user_payload, get_current_patient
from app.models.enums import AppointmentStatusEnum, USERTYPE

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_in: AppointmentCreate,
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """Create a new appointment. Only patients can book."""
    return AppointmentService.create_appointment(db, patient_id=current_patient.id, data=appointment_in)

@router.get("/me", response_model=AppointmentListResponse)
def list_my_appointments(
    status: Optional[AppointmentStatusEnum] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_payload = Depends(get_current_user_payload)
):
    """List appointments for the current user."""
    user_id = UUID(current_user_payload["user_id"])
    user_role = current_user_payload["user_type"]
    
    appointments, total = AppointmentService.list_appointments(
        db, user_id=user_id, user_role=user_role, status=status, page=page, page_size=page_size
    )
    return {"appointments": appointments, "total": total}

@router.get("/{id}", response_model=AppointmentResponse)
def get_appointment(
    id: UUID,
    db: Session = Depends(get_db),
    current_user_payload = Depends(get_current_user_payload)
):
    """Get appointment details. Enforces ownership."""
    user_id = UUID(current_user_payload["user_id"])
    user_role = current_user_payload["user_type"]
    
    return AppointmentService.get_appointment(db, appointment_id=id, user_id=user_id, user_role=user_role)

@router.patch("/{id}", response_model=AppointmentResponse)
def update_appointment(
    id: UUID,
    appointment_in: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user_payload = Depends(get_current_user_payload)
):
    """Update appointment status or details. Enforces role-based permissions."""
    user_id = UUID(current_user_payload["user_id"])
    user_role = current_user_payload["user_type"]
    
    db_obj = AppointmentService.get_appointment(db, appointment_id=id, user_id=user_id, user_role=user_role)
    
    # Permission Checks
    if user_role == USERTYPE.PATIENT:
        # Patients can only cancel
        if appointment_in.status and appointment_in.status != AppointmentStatusEnum.CANCELLED:
             raise HTTPException(status_code=403, detail="Patients can only cancel appointments")
        # Patients cannot update notes or meeting link
        if appointment_in.notes or appointment_in.meeting_link:
            raise HTTPException(status_code=403, detail="Patients cannot update notes or meeting links")
            
    elif user_role == USERTYPE.SPECIALIST:
        # Specialists can approve, complete, or cancel
        # Specialists can update notes and meeting links
        pass
    
    return AppointmentService.update_appointment(db, db_obj=db_obj, data=appointment_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    id: UUID,
    db: Session = Depends(get_db),
    current_user_payload = Depends(get_current_user_payload)
):
    """Delete an appointment. Only Admin or Owner can delete (simplified)."""
    user_id = UUID(current_user_payload["user_id"])
    user_role = current_user_payload["user_type"]
    
    db_obj = AppointmentService.get_appointment(db, appointment_id=id, user_id=user_id, user_role=user_role)
    
    # Only Admin or Owner can delete
    if user_role != USERTYPE.ADMIN.value and str(db_obj.patient_id) != str(user_id):
         raise HTTPException(status_code=403, detail="Not enough permissions to delete this appointment")
         
    AppointmentService.delete_appointment(db, db_obj=db_obj)
    return None
