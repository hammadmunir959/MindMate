"""
Appointment & Review Models
===========================
Simplified appointment booking and review system.
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Date, Time,
    ForeignKey, Enum, Index, Text, Numeric, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models_new.base import (
    BaseModel, AppointmentType, AppointmentStatus, 
    PaymentStatus, ConsultationMode
)


class Appointment(BaseModel):
    """
    Appointment booking between patient and specialist.
    Includes payment tracking and session notes.
    """
    __tablename__ = "appointments"
    
    # Participants
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False
    )
    specialist_id = Column(
        UUID(as_uuid=True),
        ForeignKey('specialists.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Scheduling
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=50)
    
    # Type
    appointment_type = Column(
        Enum(AppointmentType),
        default=AppointmentType.CONSULTATION
    )
    consultation_mode = Column(
        Enum(ConsultationMode),
        default=ConsultationMode.VIRTUAL
    )
    
    # Status
    status = Column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.PENDING
    )
    
    # Payment
    fee_amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING
    )
    payment_receipt = Column(String(500), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Meeting details
    meeting_link = Column(String(500), nullable=True)
    meeting_id = Column(String(100), nullable=True)
    
    # Notes
    patient_notes = Column(Text, nullable=True)
    specialist_notes = Column(Text, nullable=True)
    
    # Linked assessment
    assessment_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey('assessment_sessions.id', ondelete='SET NULL'),
        nullable=True
    )
    
    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Relationships
    patient = relationship(
        "Patient",
        back_populates="appointments",
        foreign_keys=[patient_id]
    )
    specialist = relationship(
        "Specialist",
        back_populates="appointments",
        foreign_keys=[specialist_id]
    )
    assessment_session = relationship("AssessmentSession")
    review = relationship(
        "SpecialistReview",
        back_populates="appointment",
        uselist=False
    )
    
    __table_args__ = (
        Index('idx_appointments_patient', 'patient_id'),
        Index('idx_appointments_specialist', 'specialist_id'),
        Index('idx_appointments_date', 'scheduled_date'),
        Index('idx_appointments_status', 'status'),
        Index('idx_appointments_upcoming', 'specialist_id', 'scheduled_date', 'status'),
    )
    
    def __repr__(self):
        return f"<Appointment {self.scheduled_date} ({self.status.value})>"


class SpecialistReview(BaseModel):
    """
    Patient review of specialist after appointment.
    Includes overall and aspect-specific ratings.
    """
    __tablename__ = "specialist_reviews"
    
    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey('appointments.id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    specialist_id = Column(
        UUID(as_uuid=True),
        ForeignKey('specialists.id', ondelete='CASCADE'),
        nullable=False
    )
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Review content
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    
    # Aspect ratings (optional)
    professionalism_rating = Column(Integer, nullable=True)
    communication_rating = Column(Integer, nullable=True)
    helpfulness_rating = Column(Integer, nullable=True)
    
    # Moderation
    is_visible = Column(Boolean, default=True)
    flagged = Column(Boolean, default=False)
    flagged_reason = Column(Text, nullable=True)
    
    # Relationships
    appointment = relationship("Appointment", back_populates="review")
    specialist = relationship(
        "Specialist",
        back_populates="reviews",
        foreign_keys=[specialist_id]
    )
    patient = relationship("Patient")
    
    __table_args__ = (
        Index('idx_reviews_specialist', 'specialist_id'),
        Index('idx_reviews_patient', 'patient_id'),
        Index('idx_reviews_visible', 'specialist_id', 'is_visible'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='chk_rating_range'),
        CheckConstraint(
            'professionalism_rating IS NULL OR (professionalism_rating >= 1 AND professionalism_rating <= 5)',
            name='chk_professionalism_range'
        ),
        CheckConstraint(
            'communication_rating IS NULL OR (communication_rating >= 1 AND communication_rating <= 5)',
            name='chk_communication_range'
        ),
        CheckConstraint(
            'helpfulness_rating IS NULL OR (helpfulness_rating >= 1 AND helpfulness_rating <= 5)',
            name='chk_helpfulness_range'
        ),
    )
    
    def __repr__(self):
        return f"<Review {self.rating}/5 for specialist {self.specialist_id}>"


__all__ = ["Appointment", "SpecialistReview"]
