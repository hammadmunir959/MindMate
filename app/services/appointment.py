from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from fastapi import HTTPException, status

from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.specialist import Specialist
from app.models.enums import AppointmentStatusEnum, ConsultationModeEnum
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.email import email_service

class AppointmentService:
    """Service class for Appointment logic in app"""

    @staticmethod
    def create_appointment(db: Session, patient_id: UUID, data: AppointmentCreate) -> Appointment:
        """Creates a new appointment with collision detection"""
        
        # 1. Collision detection (Specialist and Patient)
        new_start = data.scheduled_at
        new_end = new_start + timedelta(minutes=data.duration_minutes)

        # Check for conflicts for both specialist and patient
        # Conflicts are existing appointments that overlap and are not cancelled
        conflict = db.query(Appointment).filter(
            or_(
                Appointment.specialist_id == data.specialist_id,
                Appointment.patient_id == patient_id
            ),
            Appointment.status != AppointmentStatusEnum.CANCELLED,
            and_(
                Appointment.scheduled_at < new_end,
                (Appointment.scheduled_at + Appointment.duration_minutes * timedelta(minutes=1)) > new_start
            )
        ).first()

        if conflict:
            role = "Specialist" if conflict.specialist_id == data.specialist_id else "You"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{role} already has an appointment during this time."
            )

        # 2. Create the appointment
        db_obj = Appointment(
            patient_id=patient_id,
            specialist_id=data.specialist_id,
            assessment_session_id=data.assessment_session_id,
            scheduled_at=data.scheduled_at,
            duration_minutes=data.duration_minutes,
            appointment_type=data.appointment_type,
            reason=data.reason,
            status=AppointmentStatusEnum.PENDING
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_appointment(db: Session, appointment_id: UUID, user_id: UUID, user_role: str) -> Appointment:
        """Retrieves an appointment with ownership enforcement"""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

        # Ownership check
        if user_role == "admin":
            return appointment
        
        if str(appointment.patient_id) != str(user_id) and str(appointment.specialist_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to view this appointment"
            )
            
        return appointment

    @staticmethod
    def update_appointment(db: Session, db_obj: Appointment, data: AppointmentUpdate) -> Appointment:
        """Updates appointment status and handles auto-generation of meeting links"""
        
        # Check for status change to APPROVED for ONLINE appointments
        if data.status == AppointmentStatusEnum.APPROVED and db_obj.appointment_type == ConsultationModeEnum.ONLINE:
            if not db_obj.meeting_link:
                # Generate a simple Jitsi meeting link
                db_obj.meeting_link = f"https://meet.jit.si/MindMate-{db_obj.id}"
            
            # Fetch patient and specialist info for email
            patient = db.query(Patient).filter(Patient.id == db_obj.patient_id).first()
            specialist = db.query(Specialist).filter(Specialist.id == db_obj.specialist_id).first()
            
            if patient and specialist:
                email_service.send_appointment_confirmed(
                    email=patient.email,
                    name=f"{patient.first_name} {patient.last_name}",
                    appointment_data={
                        "date": db_obj.scheduled_at.strftime("%B %d, %Y"),
                        "time": db_obj.scheduled_at.strftime("%I:%M %p"),
                        "specialist_name": f"{specialist.first_name} {specialist.last_name}",
                        "type": db_obj.appointment_type.value,
                        "meeting_link": db_obj.meeting_link
                    }
                )

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def list_appointments(
        db: Session, 
        user_id: UUID, 
        user_role: str,
        status: Optional[AppointmentStatusEnum] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Appointment], int]:
        """Lists appointments for a specific user (Patient or Specialist)"""
        
        query = db.query(Appointment)
        
        if user_role == "patient":
            query = query.filter(Appointment.patient_id == user_id)
        elif user_role == "specialist":
            query = query.filter(Appointment.specialist_id == user_id)
        # Admins can see all (or we could add filtering)

        if status:
            query = query.filter(Appointment.status == status)

        total = query.count()
        appointments = query.order_by(Appointment.scheduled_at.desc())\
                            .offset((page - 1) * page_size)\
                            .limit(page_size)\
                            .all()
        
        return appointments, total

    @staticmethod
    def delete_appointment(db: Session, db_obj: Appointment):
        """Deletes an appointment record"""
        db.delete(db_obj)
        db.commit()
