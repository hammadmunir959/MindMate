"""
Booking API Endpoints
=====================
API routes for booking and appointment management.
"""

from typing import List, Optional, Any
from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models_new.user import User
from app.services.booking_service import booking_service
from app.db.repositories_new.appointment import appointment_repo

router = APIRouter()


# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------

class BookingCreate(BaseModel):
    specialist_id: str
    date: date
    time: str  # "HH:MM" format
    notes: Optional[str] = None


class SlotResponse(BaseModel):
    date: str
    time: str
    available: bool


class AppointmentResponse(BaseModel):
    id: str
    specialist_id: str
    patient_id: str
    scheduled_date: date
    scheduled_time: str
    status: str
    notes: Optional[str]
    meeting_link: Optional[str]

    class Config:
        orm_mode = True


# -----------------------------------------------------------------------------
# Patient Endpoints
# -----------------------------------------------------------------------------

@router.get("/slots/{specialist_id}", response_model=List[SlotResponse])
def get_available_slots(
    specialist_id: str,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available slots for a specialist for the next N days.
    """
    return booking_service.get_available_slots(db, specialist_id, days)


@router.post("/book", response_model=AppointmentResponse)
def book_appointment(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Book an appointment with a specialist.
    """
    # Parse time string to time object
    try:
        t = datetime.strptime(booking.time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

    # Get patient ID from current user
    if not current_user.patient:
        raise HTTPException(status_code=400, detail="User is not a patient")
    
    appointment = booking_service.create_booking(
        db,
        patient_id=current_user.patient.id,
        specialist_id=booking.specialist_id,
        slot_date=booking.date,
        slot_time=t,
        notes=booking.notes
    )
    
    # Convert time to string for response
    return _map_appointment_response(appointment)


@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List current user's upcoming appointments.
    """
    if current_user.patient:
        apps = appointment_repo.get_upcoming_for_patient(db, current_user.patient.id)
    elif current_user.specialist:
        apps = appointment_repo.get_upcoming_for_specialist(db, current_user.specialist.id)
    else:
        apps = []
        
    return [_map_appointment_response(a) for a in apps]


# -----------------------------------------------------------------------------
# Specialist Endpoints
# -----------------------------------------------------------------------------

@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_booking(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm a booking request (Specialist only)"""
    if not current_user.specialist:
        raise HTTPException(status_code=403, detail="Only specialists can confirm bookings")
        
    appointment = booking_service.confirm_booking(
        db, current_user.specialist.id, appointment_id
    )
    return _map_appointment_response(appointment)


@router.post("/{appointment_id}/reject", response_model=AppointmentResponse)
def reject_booking(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a booking request (Specialist only)"""
    if not current_user.specialist:
        raise HTTPException(status_code=403, detail="Only specialists can reject bookings")
        
    appointment = booking_service.reject_booking(
        db, current_user.specialist.id, appointment_id
    )
    return _map_appointment_response(appointment)


def _map_appointment_response(appointment: Any) -> AppointmentResponse:
    """Helper to map SQLAlchemy object to Pydantic model"""
    return AppointmentResponse(
        id=str(appointment.id),
        specialist_id=str(appointment.specialist_id),
        patient_id=str(appointment.patient_id),
        scheduled_date=appointment.scheduled_date,
        scheduled_time=appointment.scheduled_time.strftime("%H:%M") if hasattr(appointment.scheduled_time, "strftime") else str(appointment.scheduled_time),
        status=appointment.status.value if hasattr(appointment.status, "value") else str(appointment.status),
        notes=appointment.patient_notes,
        meeting_link=appointment.meeting_link
    )
