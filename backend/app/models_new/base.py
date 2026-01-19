"""
MindMate Base Models & Enums
============================
Base model class and all PostgreSQL enumerations.
"""

from sqlalchemy import (
    Column, DateTime, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
import enum


# Base class for all models
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields.
    All models inherit from this.
    """
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


# ============================================================================
# ENUMERATIONS
# ============================================================================

class UserType(str, enum.Enum):
    """User types in the system"""
    PATIENT = "patient"
    SPECIALIST = "specialist"
    ADMIN = "admin"


class Gender(str, enum.Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class SessionStatus(str, enum.Enum):
    """Assessment session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class AssessmentPhase(str, enum.Enum):
    """Therapeutic conversation phases"""
    RAPPORT = "rapport"
    EXPLORATION = "exploration"
    DEEPENING = "deepening"
    CLOSING = "closing"


class MessageRole(str, enum.Enum):
    """Message sender roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SymptomCategory(str, enum.Enum):
    """DSM-5 symptom categories"""
    DEPRESSIVE = "depressive"
    ANXIETY = "anxiety"
    TRAUMA = "trauma"
    BIPOLAR = "bipolar"
    OCD = "ocd"
    EATING = "eating"
    SLEEP = "sleep"
    SUBSTANCE = "substance"
    OTHER = "other"


class Frequency(str, enum.Enum):
    """Symptom frequency levels"""
    DAILY = "daily"
    WEEKLY = "weekly"
    OCCASIONALLY = "occasionally"
    RARELY = "rarely"


class SeverityLevel(str, enum.Enum):
    """Severity classification"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class RiskLevel(str, enum.Enum):
    """Risk assessment levels"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DiagnosisType(str, enum.Enum):
    """Source of diagnosis"""
    AI_GENERATED = "ai_generated"
    SPECIALIST_CONFIRMED = "specialist_confirmed"
    SPECIALIST_REVISED = "specialist_revised"


class SpecialistType(str, enum.Enum):
    """Types of mental health specialists"""
    PSYCHIATRIST = "psychiatrist"
    CLINICAL_PSYCHOLOGIST = "clinical_psychologist"
    COUNSELOR = "counselor"
    THERAPIST = "therapist"


class Specialization(str, enum.Enum):
    """Areas of specialization"""
    DEPRESSION = "depression"
    ANXIETY = "anxiety"
    TRAUMA_PTSD = "trauma_ptsd"
    OCD = "ocd"
    BIPOLAR = "bipolar"
    EATING_DISORDERS = "eating_disorders"
    COUPLES = "couples"
    FAMILY = "family"
    CHILD_ADOLESCENT = "child_adolescent"
    ADDICTION = "addiction"
    GRIEF = "grief"
    ANGER_MANAGEMENT = "anger_management"


class ConsultationMode(str, enum.Enum):
    """Consultation delivery modes"""
    VIRTUAL = "virtual"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"


class ApprovalStatus(str, enum.Enum):
    """Specialist approval workflow status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class DocumentType(str, enum.Enum):
    """Types of specialist documents"""
    DEGREE = "degree"
    LICENSE = "license"
    PMDC_CERTIFICATE = "pmdc_certificate"
    CNIC = "cnic"
    PROFILE_PHOTO = "profile_photo"


class DocumentStatus(str, enum.Enum):
    """Document verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class AppointmentType(str, enum.Enum):
    """Types of appointments"""
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    ASSESSMENT_REVIEW = "assessment_review"


class AppointmentStatus(str, enum.Enum):
    """Appointment lifecycle status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PaymentStatus(str, enum.Enum):
    """Payment status"""
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"


class AdminRole(str, enum.Enum):
    """Admin role levels"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"


# Export all
__all__ = [
    "Base",
    "BaseModel",
    "UserType",
    "Gender",
    "SessionStatus",
    "AssessmentPhase",
    "MessageRole",
    "SymptomCategory",
    "Frequency",
    "SeverityLevel",
    "RiskLevel",
    "DiagnosisType",
    "SpecialistType",
    "Specialization",
    "ConsultationMode",
    "ApprovalStatus",
    "DocumentType",
    "DocumentStatus",
    "AppointmentType",
    "AppointmentStatus",
    "PaymentStatus",
    "AdminRole",
]
