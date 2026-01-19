"""
Appointment Repository
======================
Data access for Appointments.
"""

from typing import Optional, List, Dict
from datetime import date, time
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from app.db.repositories_new.base import BaseRepository
from app.models_new.appointment import Appointment, AppointmentStatus


class AppointmentRepository(BaseRepository[Appointment, dict, dict]):
    """
    Repository for Appointment operations.
    """
    
    def get_upcoming_for_patient(
        self, db: Session, patient_id: str
    ) -> List[Appointment]:
        """Get upcoming appointments for patient"""
        return db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            or_(
                Appointment.status == AppointmentStatus.PENDING,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        ).order_by(Appointment.scheduled_date, Appointment.scheduled_time).all()
        
    def get_upcoming_for_specialist(
        self, db: Session, specialist_id: str
    ) -> List[Appointment]:
        """Get upcoming appointments for specialist"""
        return db.query(Appointment).filter(
            Appointment.specialist_id == specialist_id,
            or_(
                Appointment.status == AppointmentStatus.PENDING,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        ).order_by(Appointment.scheduled_date, Appointment.scheduled_time).all()
    
    def check_availability(
        self, 
        db: Session, 
        specialist_id: str, 
        scheduled_date: date, 
        scheduled_time: time
    ) -> bool:
        """
        Check if a slot is available (no conflicting CONFIRMED appointments).
        Returns True if available, False if taken.
        """
        count = db.query(Appointment).filter(
            Appointment.specialist_id == specialist_id,
            Appointment.scheduled_date == scheduled_date,
            Appointment.scheduled_time == scheduled_time,
            Appointment.status == AppointmentStatus.CONFIRMED
        ).count()
        return count == 0

    def update_status(
        self, 
        db: Session, 
        appointment_id: str, 
        status: AppointmentStatus
    ) -> Optional[Appointment]:
        """Update appointment status"""
        appointment = self.get(db, appointment_id)
        if appointment:
            appointment.status = status
            db.commit()
            db.refresh(appointment)
        return appointment


appointment_repo = AppointmentRepository(Appointment)
