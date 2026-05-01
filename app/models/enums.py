import enum

class USERTYPE(str, enum.Enum):
    """Enumeration for user types"""
    ADMIN = "admin"
    PATIENT = "patient"
    SPECIALIST = "specialist"

class GenderEnum(str, enum.Enum):
    """Gender identity options"""
    MALE = "male"
    FEMALE = "female"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"

class AdminRoleEnum(str, enum.Enum):
    """Simple admin role hierarchy"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"

class AccountStatusEnum(str, enum.Enum):
    """Unified Account/Record Status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

class ConsultationModeEnum(str, enum.Enum):
    """Consultation delivery modes"""
    ONLINE = "online"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"

class LanguageEnum(str, enum.Enum):
    """Language options for Pakistan context"""
    ENGLISH = "english"
    URDU = "urdu"
    PUNJABI = "punjabi"
    SINDHI = "sindhi"
    PASHTO = "pashto"

class PaymentMethodEnum(str, enum.Enum):
    """Payment method preferences"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    JAZZCASH = "jazzcash"
    EASYPAISA = "easypaisa"
    CARD = "card"
    INSURANCE = "insurance"

class UrgencyLevelEnum(str, enum.Enum):
    """Appointment urgency levels"""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    STANDARD = "standard"
    FLEXIBLE = "flexible"

class SpecialistTypeEnum(str, enum.Enum):
    """Mental health specialist types"""
    PSYCHIATRIST = "psychiatrist"
    PSYCHOLOGIST = "psychologist" 
    COUNSELOR = "counselor"
    THERAPIST = "therapist"
    SOCIAL_WORKER = "social_worker"

class AvailabilityStatusEnum(str, enum.Enum):
    """Specialist availability for booking"""
    ACCEPTING_NEW_PATIENTS = "accepting_new_patients"
    WAITLIST_ONLY = "waitlist_only"
    NOT_ACCEPTING_NEW_PATIENTS = "not_accepting_new_patients"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"

class ApprovalStatusEnum(str, enum.Enum):
    """Admin approval status for specialists/documents"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"

class EmailVerificationStatusEnum(str, enum.Enum):
    """Email verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"

class DocumentTypeEnum(str, enum.Enum):
    """Document types for approval"""
    DEGREE = "degree"
    LICENSE = "license"
    CERTIFICATION = "certification"
    IDENTITY_CARD = "identity_card"
    EXPERIENCE_LETTER = "experience_letter"
    OTHER = "other"

class TherapyMethodEnum(str, enum.Enum):
    """Therapy methods and approaches (Unified)"""
    CBT = "cbt"
    DBT = "dbt"
    ACT = "act"
    PSYCHOANALYSIS = "psychoanalysis"
    EMDR = "emdr"
    HUMANISTIC = "humanistic"
    FAMILY_THERAPY = "family_therapy"
    GROUP_THERAPY = "group_therapy"
    MINDFULNESS = "mindfulness"
    PSYCHODYNAMIC = "psychodynamic"
    SOLUTION_FOCUSED = "solution_focused"
    NARRATIVE_THERAPY = "narrative_therapy"

class ForumCategoryEnum(str, enum.Enum):
    """Core categories for the community forum"""
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    RELATIONSHIPS = "relationships"
    ADDICTION = "addiction"
    TRAUMA = "trauma"
    GENERAL = "general"
    OTHER = "other"

class AppointmentStatusEnum(str, enum.Enum):
    """Core appointment states"""
    PENDING = "pending"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
