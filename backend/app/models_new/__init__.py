"""
MindMate Database Models v2
===========================
Fresh, optimized database models for multi-agent mental health platform.

Database: mindmate_v2 (PostgreSQL)
Tables: 13 (down from 55+)

Architecture:
- Unified User authentication
- JSONB for flexible preferences/schedules
- Multi-agent optimized (symptoms, diagnoses, matches)
- Proper indexing and constraints
"""

# Configuration
from app.models_new.config import db_settings, get_db_settings

# Base and Enums
from app.models_new.base import (
    Base,
    BaseModel,
    # User types
    UserType,
    Gender,
    # Session/Assessment
    SessionStatus,
    AssessmentPhase,
    MessageRole,
    # Clinical
    SymptomCategory,
    Frequency,
    SeverityLevel,
    RiskLevel,
    DiagnosisType,
    # Specialist
    SpecialistType,
    Specialization,
    ConsultationMode,
    ApprovalStatus,
    DocumentType,
    DocumentStatus,
    # Appointment
    AppointmentType,
    AppointmentStatus,
    PaymentStatus,
    # Admin
    AdminRole,
)

# Auth Models
from app.models_new.user import (
    User,
    PasswordResetToken,
)

# Patient Model
from app.models_new.patient import (
    Patient,
)

# Assessment Models (Multi-Agent)
from app.models_new.assessment import (
    AssessmentSession,
    ConversationMessage,
    ExtractedSymptom,
    Diagnosis,
)

# Specialist Models
from app.models_new.specialist import (
    Specialist,
    SpecialistDocument,
    SpecialistMatch,
)

# Appointment Models
from app.models_new.appointment import (
    Appointment,
    SpecialistReview,
)

# Admin Model
from app.models_new.admin import (
    Admin,
)


__all__ = [
    # Config
    "db_settings",
    "get_db_settings",
    
    # Base
    "Base",
    "BaseModel",
    
    # Enums
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
    
    # Models (13 tables)
    "User",
    "PasswordResetToken",
    "Patient",
    "AssessmentSession",
    "ConversationMessage",
    "ExtractedSymptom",
    "Diagnosis",
    "Specialist",
    "SpecialistDocument",
    "SpecialistMatch",
    "Appointment",
    "SpecialistReview",
    "Admin",
]
