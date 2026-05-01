from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base, BaseModel
from .enums import USERTYPE, GenderEnum, LanguageEnum, AccountStatusEnum

class Patient(Base, BaseModel):
    """Core patient model including authentication"""
    __tablename__ = "patients"

    # User Type
    user_type = Column(Enum(USERTYPE), nullable=False, default=USERTYPE.PATIENT)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    
    # Location
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Pakistan")
    

    # Contact & Authentication
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20))
    hashed_password = Column(String, nullable=True)
    
    # Account Status
    account_status = Column(Enum(AccountStatusEnum), default=AccountStatusEnum.ACTIVE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_otp = Column(String(10), nullable=True)
    otp_created_at = Column(DateTime, nullable=True)
    
    # Relationships
    assessment_sessions = relationship("AssessmentSession", back_populates="patient", cascade="all, delete-orphan")


class AssessmentSession(Base, BaseModel):
    """Stores the multi-agent session data and assessments for a patient."""
    __tablename__ = "assessment_sessions"

    patient_id = Column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String, nullable=False, index=True)
    
    # Session state
    is_completed = Column(Boolean, default=False)
    interview_summary = Column(String, nullable=True)
    
    # Agent Outputs stored as JSON
    symptoms = Column(JSON, nullable=True)
    conversation_history = Column(JSON, nullable=True)
    clinical_report = Column(JSON, nullable=True)
    diagnoser_results = Column(JSON, nullable=True)
    treatment_plan = Column(JSON, nullable=True)
    recommended_specialists = Column(JSON, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="assessment_sessions")
