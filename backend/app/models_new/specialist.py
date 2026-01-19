"""
Specialist Models
=================
Specialist profile with consolidated availability and documents.
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, 
    Enum, Index, Text, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.models_new.base import (
    BaseModel, SpecialistType, Specialization, ConsultationMode,
    ApprovalStatus, DocumentType, DocumentStatus
)


class Specialist(BaseModel):
    """
    Specialist profile with professional info and availability.
    Uses JSONB for weekly schedule flexibility.
    """
    __tablename__ = "specialists"
    
    # Link to unified users table
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    
    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(50), nullable=True)  # Dr., Prof., etc.
    
    # Professional info
    specialist_type = Column(Enum(SpecialistType), nullable=False)
    specializations = Column(ARRAY(String(50)), nullable=False, default=[])
    
    # Registration
    license_number = Column(String(100), nullable=True)
    pmdc_number = Column(String(100), nullable=True)  # Pakistan specific
    
    # Experience
    experience_years = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    professional_statement = Column(Text, nullable=True)
    
    # Consultation
    fee_per_session = Column(Numeric(10, 2), nullable=True)
    session_duration = Column(Integer, default=50)  # minutes
    consultation_modes = Column(
        ARRAY(String(20)),
        default=["virtual"]
    )
    
    # Languages
    languages = Column(ARRAY(String(50)), default=["english"])
    
    # Location
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Gender (for patient preference matching)
    gender = Column(String(20), nullable=True)
    
    # Approval status
    approval_status = Column(
        Enum(ApprovalStatus),
        default=ApprovalStatus.PENDING
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(
        UUID(as_uuid=True),
        ForeignKey('admins.id', ondelete='SET NULL'),
        nullable=True
    )
    rejection_reason = Column(Text, nullable=True)
    
    # Stats (denormalized for performance)
    total_reviews = Column(Integer, default=0)
    average_rating = Column(Numeric(2, 1), default=0.0)
    total_patients = Column(Integer, default=0)
    
    # Weekly schedule (JSONB for flexibility)
    weekly_schedule = Column(JSONB, default={})
    """
    Structure:
    {
        "monday": [{"start": "09:00", "end": "13:00"}, {"start": "14:00", "end": "17:00"}],
        "tuesday": [{"start": "09:00", "end": "17:00"}],
        ...
    }
    """
    
    # Relationships
    user = relationship("User", back_populates="specialist", foreign_keys=[user_id])
    documents = relationship(
        "SpecialistDocument",
        back_populates="specialist",
        cascade="all, delete-orphan"
    )
    appointments = relationship(
        "Appointment",
        back_populates="specialist",
        foreign_keys="Appointment.specialist_id"
    )
    reviews = relationship(
        "SpecialistReview",
        back_populates="specialist",
        foreign_keys="SpecialistReview.specialist_id"
    )
    
    __table_args__ = (
        Index('idx_specialists_user', 'user_id'),
        Index('idx_specialists_type', 'specialist_type'),
        Index('idx_specialists_status', 'approval_status'),
        Index('idx_specialists_city', 'city'),
        Index('idx_specialists_approved', 'approval_status', 'city'),
    )
    
    @property
    def full_name(self) -> str:
        """Get specialist's full name with title"""
        if self.title:
            return f"{self.title} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_approved(self) -> bool:
        """Check if specialist is approved"""
        return self.approval_status == ApprovalStatus.APPROVED
    
    def __repr__(self):
        return f"<Specialist {self.full_name} ({self.specialist_type.value})>"


class SpecialistDocument(BaseModel):
    """
    Specialist verification documents.
    Tracks document upload and verification status.
    """
    __tablename__ = "specialist_documents"
    
    specialist_id = Column(
        UUID(as_uuid=True),
        ForeignKey('specialists.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Document info
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    
    # Verification
    status = Column(
        Enum(DocumentStatus),
        default=DocumentStatus.PENDING
    )
    verified_by = Column(
        UUID(as_uuid=True),
        ForeignKey('admins.id', ondelete='SET NULL'),
        nullable=True
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    specialist = relationship("Specialist", back_populates="documents")
    verifier = relationship("Admin", foreign_keys=[verified_by])
    
    __table_args__ = (
        Index('idx_documents_specialist', 'specialist_id'),
        Index('idx_documents_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Document {self.document_type.value} ({self.status.value})>"


class SpecialistMatch(BaseModel):
    """
    Specialist matches generated by Matcher Agent.
    Links assessment sessions to recommended specialists.
    """
    __tablename__ = "specialist_matches"
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey('assessment_sessions.id', ondelete='CASCADE'),
        nullable=False
    )
    specialist_id = Column(
        UUID(as_uuid=True),
        ForeignKey('specialists.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Match details
    match_score = Column(Numeric(3, 2), nullable=False)
    rank = Column(Integer, nullable=False)
    
    # Match reasons (stored as array)
    match_reasons = Column(ARRAY(Text), nullable=False, default=[])
    
    # User action
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    selected = Column(Boolean, default=False)
    
    # Relationships
    session = relationship("AssessmentSession", back_populates="specialist_matches")
    specialist = relationship("Specialist")
    
    __table_args__ = (
        Index('idx_matches_session', 'session_id'),
        Index('idx_matches_specialist', 'specialist_id'),
        Index('idx_matches_rank', 'session_id', 'rank'),
    )
    
    def __repr__(self):
        return f"<Match rank={self.rank} score={self.match_score}>"


__all__ = ["Specialist", "SpecialistDocument", "SpecialistMatch"]
