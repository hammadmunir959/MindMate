"""
Assessment Models
=================
Multi-agent assessment workflow models (sessions, messages, symptoms, diagnoses).
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, 
    Enum, Index, Text, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.models_new.base import (
    BaseModel, SessionStatus, AssessmentPhase, MessageRole,
    SymptomCategory, Frequency, SeverityLevel, RiskLevel, DiagnosisType
)


class AssessmentSession(BaseModel):
    """
    Assessment session tracking.
    Core table for multi-agent workflow state.
    """
    __tablename__ = "assessment_sessions"
    
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Session state
    status = Column(
        Enum(SessionStatus),
        nullable=False,
        default=SessionStatus.ACTIVE
    )
    current_phase = Column(
        Enum(AssessmentPhase),
        default=AssessmentPhase.RAPPORT
    )
    
    # Progress tracking
    message_count = Column(Integer, default=0)
    symptom_count = Column(Integer, default=0)
    
    # Risk assessment
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.NONE)
    
    # State snapshot (for workflow resume)
    state_snapshot = Column(JSONB, default={})
    """
    Structure:
    {
        "topics_explored": ["anxiety", "sleep"],
        "risk_flags": [],
        "last_agent": "therapist"
    }
    """
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default="now()")
    last_active_at = Column(DateTime(timezone=True), server_default="now()")
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="assessment_sessions")
    messages = relationship(
        "ConversationMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at"
    )
    symptoms = relationship(
        "ExtractedSymptom",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    diagnoses = relationship(
        "Diagnosis",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    specialist_matches = relationship(
        "SpecialistMatch",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_sessions_patient', 'patient_id'),
        Index('idx_sessions_status', 'status'),
        Index('idx_sessions_active', 'patient_id', 'status'),
    )
    
    def __repr__(self):
        return f"<AssessmentSession {self.id} ({self.status.value})>"


class ConversationMessage(BaseModel):
    """
    Conversation history for assessment sessions.
    Stores all messages between user and therapist agent.
    """
    __tablename__ = "conversation_messages"
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey('assessment_sessions.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Message content
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Context
    phase = Column(Enum(AssessmentPhase), nullable=True)
    
    # Metadata (agent info, sentiment, topics)
    msg_metadata = Column("metadata", JSONB, default={})
    """
    Structure:
    {
        "agent": "therapist",
        "risk_detected": false,
        "sentiment": 0.7,
        "topics": ["anxiety", "work"]
    }
    """
    
    # Relationships
    session = relationship("AssessmentSession", back_populates="messages")
    
    __table_args__ = (
        Index('idx_messages_session', 'session_id'),
        Index('idx_messages_session_order', 'session_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Message {self.role.value}: {self.content[:30]}...>"


class ExtractedSymptom(BaseModel):
    """
    Symptoms extracted by SRA agent.
    Continuous async extraction during conversation.
    """
    __tablename__ = "extracted_symptoms"
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey('assessment_sessions.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Symptom identification
    symptom_name = Column(String(200), nullable=False)
    category = Column(Enum(SymptomCategory), nullable=False)
    
    # Clinical attributes
    severity = Column(Numeric(3, 2), nullable=False, default=0.5)
    frequency = Column(Enum(Frequency), nullable=True)
    duration = Column(String(50), nullable=True)  # 'days', 'weeks', 'months'
    
    # DSM-5 mapping
    dsm5_criteria = Column(ARRAY(String(20)), default=[])
    
    # Source tracking
    source_message_id = Column(
        UUID(as_uuid=True),
        ForeignKey('conversation_messages.id', ondelete='SET NULL'),
        nullable=True
    )
    source_text = Column(Text, nullable=True)
    extraction_method = Column(String(20), default="ner")  # 'ner', 'llm', 'both'
    
    # Confidence
    confidence = Column(Numeric(3, 2), default=0.8)
    mention_count = Column(Integer, default=1)
    
    # Timing
    first_mentioned = Column(DateTime(timezone=True), server_default="now()")
    last_mentioned = Column(DateTime(timezone=True), server_default="now()")
    
    # Relationships
    session = relationship("AssessmentSession", back_populates="symptoms")
    source_message = relationship("ConversationMessage")
    
    __table_args__ = (
        Index('idx_symptoms_session', 'session_id'),
        Index('idx_symptoms_category', 'category'),
        Index('idx_symptoms_severity', 'severity'),
        Index('idx_symptoms_unique', 'session_id', 'symptom_name', unique=True),
    )
    
    def __repr__(self):
        return f"<Symptom {self.symptom_name} ({self.severity})>"


class Diagnosis(BaseModel):
    """
    Diagnosis generated by Diagnosis Agent.
    DSM-5 compliant with confidence scoring.
    """
    __tablename__ = "diagnoses"
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey('assessment_sessions.id', ondelete='CASCADE'),
        nullable=False
    )
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Diagnosis details
    disorder_code = Column(String(20), nullable=False)  # ICD-10/DSM-5
    disorder_name = Column(String(200), nullable=False)
    category = Column(Enum(SymptomCategory), nullable=False)
    
    # Confidence and severity
    confidence = Column(Numeric(3, 2), nullable=False)
    severity = Column(Enum(SeverityLevel), nullable=False)
    
    # Criteria details
    criteria_met = Column(ARRAY(String(20)), nullable=False)
    criteria_total = Column(Integer, nullable=False)
    
    # Diagnosis type
    is_primary = Column(Boolean, default=False)
    diagnosis_type = Column(
        Enum(DiagnosisType),
        default=DiagnosisType.AI_GENERATED
    )
    
    # Clinical notes
    clinical_notes = Column(Text, nullable=True)
    clinical_report = Column(Text, nullable=True)
    
    # Specialist review
    reviewed_by = Column(
        UUID(as_uuid=True),
        ForeignKey('specialists.id', ondelete='SET NULL'),
        nullable=True
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timing
    diagnosed_at = Column(DateTime(timezone=True), server_default="now()")
    
    # Relationships
    session = relationship("AssessmentSession", back_populates="diagnoses")
    patient = relationship("Patient")
    reviewer = relationship("Specialist", foreign_keys=[reviewed_by])
    
    __table_args__ = (
        Index('idx_diagnoses_session', 'session_id'),
        Index('idx_diagnoses_patient', 'patient_id'),
        Index('idx_diagnoses_primary', 'session_id', 'is_primary'),
    )
    
    def __repr__(self):
        return f"<Diagnosis {self.disorder_name} ({self.confidence})>"


__all__ = [
    "AssessmentSession",
    "ConversationMessage",
    "ExtractedSymptom",
    "Diagnosis",
]
