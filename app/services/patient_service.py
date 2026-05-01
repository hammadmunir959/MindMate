from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.core.security import get_password_hash, generate_otp
from app.services.email import email_service
from datetime import datetime, timezone

class PatientService:
    @staticmethod
    def get_patient(db: Session, patient_id: UUID) -> Patient:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return patient

    @staticmethod
    def get_patient_by_email(db: Session, email: str) -> Patient:
        return db.query(Patient).filter(Patient.email == email).first()

    @staticmethod
    def create_patient(db: Session, patient_in: PatientCreate) -> Patient:
        # Check if email is already registered
        if PatientService.get_patient_by_email(db, patient_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Hash password and create patient
        patient_data = patient_in.model_dump(exclude={"password"})
        hashed_password = get_password_hash(patient_in.password)
        
        # Generate verification OTP
        otp = generate_otp()
        
        patient = Patient(
            **patient_data, 
            hashed_password=hashed_password,
            verification_otp=otp,
            otp_created_at=datetime.now(timezone.utc)
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Send verification email
        email_service.send_verification_otp(
            email=patient.email,
            name=f"{patient.first_name} {patient.last_name}",
            otp=otp
        )

        return patient

    @staticmethod
    def update_patient(db: Session, patient_id: UUID, patient_in: PatientUpdate) -> Patient:
        patient = PatientService.get_patient(db, patient_id)
        
        update_data = patient_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
            
        db.commit()
        db.refresh(patient)
        return patient
        
    @staticmethod
    def list_patients(db: Session, skip: int = 0, limit: int = 100) -> list[Patient]:
        return db.query(Patient).filter(Patient.is_deleted == False).offset(skip).limit(limit).all()

    @staticmethod
    def list_assessments(
        db: Session, 
        patient_id: UUID, 
        page: int = 1, 
        page_size: int = 10,
        is_completed: Optional[bool] = None
    ) -> tuple[list, int]:
        """Lists assessment sessions for a patient with pagination and filtering."""
        from app.models.patient import AssessmentSession
        query = db.query(AssessmentSession).filter(AssessmentSession.patient_id == patient_id)
        
        if is_completed is not None:
            query = query.filter(AssessmentSession.is_completed == is_completed)
            
        total = query.count()
        results = query.order_by(AssessmentSession.created_at.desc())\
                       .offset((page - 1) * page_size)\
                       .limit(page_size)\
                       .all()
        return results, total

    @staticmethod
    def get_patients_by_specialist(db: Session, specialist_id: UUID) -> list[Patient]:
        """Returns distinct patients who have at least one appointment with the given specialist."""
        from app.models.appointment import Appointment
        return (
            db.query(Patient)
            .join(Appointment, Appointment.patient_id == Patient.id)
            .filter(
                Appointment.specialist_id == specialist_id,
                Patient.is_deleted == False
            )
            .distinct()
            .all()
        )

    @staticmethod
    def is_patient_associated_with_specialist(db: Session, patient_id: UUID, specialist_id: UUID) -> bool:
        """Checks if a specialist has at least one appointment with a given patient."""
        from app.models.appointment import Appointment
        return db.query(Appointment).filter(
            Appointment.specialist_id == specialist_id,
            Appointment.patient_id == patient_id
        ).first() is not None
