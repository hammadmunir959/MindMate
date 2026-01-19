"""
Patient Model
=============
Simplified patient profile with JSONB preferences.
"""

from sqlalchemy import (
    Column, String, Date, Enum, ForeignKey, Index, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models_new.base import BaseModel, Gender


class Patient(BaseModel):
    """
    Patient profile with demographics and preferences.
    Uses JSONB for flexible preference storage.
    """
    __tablename__ = "patients"
    
    # Link to unified users table
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    
    # Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Location
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Pakistan")
    
    # Preferences (JSONB for flexibility)
    preferences = Column(JSONB, default={})
    """
    Structure:
    {
        "language": "english",
        "consultation_mode": "virtual",
        "specialist_gender": "female",
        "therapy_approach": "cbt",
        "max_fee": 5000
    }
    """
    
    # Emergency contact
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Profile
    bio = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="patient", foreign_keys=[user_id])
    assessment_sessions = relationship(
        "AssessmentSession",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    appointments = relationship(
        "Appointment",
        back_populates="patient",
        foreign_keys="Appointment.patient_id",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_patients_user', 'user_id'),
        Index('idx_patients_name', 'first_name', 'last_name'),
        Index('idx_patients_city', 'city'),
    )
    
    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Patient {self.full_name}>"


__all__ = ["Patient"]
