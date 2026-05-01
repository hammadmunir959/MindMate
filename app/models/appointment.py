from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
from .base import Base, BaseModel
from .enums import AppointmentStatusEnum, ConsultationModeEnum

class Appointment(Base, BaseModel):
    """Simplified appointment model for app"""
    __tablename__ = "appointments"

    # Foreign Keys
    patient_id = Column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    specialist_id = Column(ForeignKey("specialists.id", ondelete="CASCADE"), nullable=False)
    assessment_session_id = Column(ForeignKey("assessment_sessions.id", ondelete="SET NULL"), nullable=True)

    # Core Fields
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    status = Column(Enum(AppointmentStatusEnum), nullable=False, default=AppointmentStatusEnum.PENDING)
    appointment_type = Column(Enum(ConsultationModeEnum), nullable=False, default=ConsultationModeEnum.ONLINE)

    # Content
    reason = Column(Text, nullable=True)  # Patient's reason for booking
    notes = Column(Text, nullable=True)   # Specialist's notes
    meeting_link = Column(String(500), nullable=True)  # Auto-generated for ONLINE appointments

    # Relationships
    patient = relationship("Patient", backref="appointments")
    specialist = relationship("Specialist", backref="appointments")
    assessment_session = relationship("AssessmentSession", backref="appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, status={self.status}, scheduled_at={self.scheduled_at})>"
