"""
MindMate Core Types
===================
Unified type definitions for the agent architecture.
Following system design checklist.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple


# =============================================================================
# ENUMS
# =============================================================================

class ResponseType(Enum):
    """SCID question response types"""
    YES_NO = "yes_no"
    MCQ = "mcq"           # Multiple choice (4 options)
    SCALE = "scale"       # Numeric scale
    TEXT = "text"         # Free text
    DATE = "date"


class Severity(Enum):
    """Symptom/diagnosis severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class ConversationPhase(Enum):
    """Therapeutic conversation phases"""
    RAPPORT = "rapport"           # First 3-5 exchanges
    EXPLORATION = "exploration"   # Main conversation
    DEEPENING = "deepening"       # When symptoms emerge
    CLOSING = "closing"           # Wrapping up


class RiskLevel(Enum):
    """Risk assessment levels"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ModuleStatus(Enum):
    """Interview module status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================

@dataclass
class Symptom:
    """Extracted symptom with DSM-5 mapping"""
    name: str
    severity: float = 0.5                    # 0.0-1.0
    confidence: float = 1.0                  # Extraction confidence
    category: str = ""                       # DSM category
    dsm_criteria_id: Optional[str] = None    # e.g., "MDD_A1"
    frequency: Optional[str] = None          # "daily", "weekly", etc.
    duration: Optional[str] = None           # "2 weeks", "3 months"
    first_mentioned: datetime = field(default_factory=datetime.utcnow)
    source_message: Optional[str] = None


@dataclass
class SCIDQuestion:
    """Structured clinical interview question"""
    id: str                                  # e.g., "MDD_01"
    text: str                                # User-facing question
    response_type: ResponseType = ResponseType.TEXT
    options: List[str] = field(default_factory=list)  # For MCQ
    scale_range: Tuple[int, int] = (1, 10)
    
    # DSM mapping
    dsm_criterion_id: str = ""               # Maps to DSM criteria
    category: str = ""                       # Module category
    linked_modules: List[str] = field(default_factory=list)
    
    # Routing logic
    priority: int = 3                        # 1=Critical, 2=High, 3=Medium, 4=Low
    skip_if_no: bool = False                 # Skip follow-ups if "no"
    follow_up_ids: List[str] = field(default_factory=list)
    
    # Metadata
    keywords: List[str] = field(default_factory=list)


@dataclass
class ProcessedResponse:
    """LLM-processed user response"""
    raw_text: str
    interpreted_value: Any = None            # yes/no, scale value, etc.
    confidence: float = 1.0
    
    # Extracted clinical data
    extracted_symptoms: List[str] = field(default_factory=list)
    severity_indicators: Dict[str, float] = field(default_factory=dict)
    duration_mentioned: Optional[str] = None
    frequency_mentioned: Optional[str] = None
    triggers_mentioned: List[str] = field(default_factory=list)
    
    # DSM mapping
    criteria_supported: List[str] = field(default_factory=list)
    criteria_contradicted: List[str] = field(default_factory=list)
    
    # Routing hints
    suggested_follow_ups: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)


@dataclass
class ConversationState:
    """Shared state across all agents (per session)"""
    session_id: str
    patient_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    # Conversation tracking
    messages: List[Dict[str, str]] = field(default_factory=list)
    phase: ConversationPhase = ConversationPhase.RAPPORT
    active_topics: List[str] = field(default_factory=list)
    emotional_tone: str = "neutral"
    
    # Symptom data (SRA owns)
    symptoms: List[Symptom] = field(default_factory=list)
    dsm_criteria_met: Dict[str, List[str]] = field(default_factory=dict)
    
    # Interview tracking
    interview_module: Optional[str] = None
    questions_asked: List[str] = field(default_factory=list)
    screening_scores: Dict[str, float] = field(default_factory=dict)
    modules_triggered: List[str] = field(default_factory=list)
    
    # Diagnosis data
    diagnosis_ready: bool = False
    primary_diagnosis: Optional[Dict] = None
    differential_diagnoses: List[Dict] = field(default_factory=list)
    
    # Control flags
    risk_level: RiskLevel = RiskLevel.NONE
    requires_escalation: bool = False
    session_complete: bool = False
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()})
    
    def add_symptom(self, symptom: Symptom):
        # Update existing or add new
        for i, existing in enumerate(self.symptoms):
            if existing.name.lower() == symptom.name.lower():
                if symptom.severity > existing.severity:
                    self.symptoms[i] = symptom
                return
        self.symptoms.append(symptom)
    
    def should_trigger_diagnosis(self) -> bool:
        """Check if enough data for diagnosis"""
        return (
            len(self.symptoms) >= 3 and
            len(self.messages) >= 10 and
            any(s.severity >= 0.6 for s in self.symptoms)
        )


# =============================================================================
# AGENT OUTPUTS
# =============================================================================

@dataclass
class AgentOutput:
    """Standard output from any agent"""
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    requires_handoff: bool = False
    handoff_to: Optional[str] = None


@dataclass
class TherapistOutput(AgentOutput):
    """Therapist agent specific output"""
    message: str = ""
    phase: ConversationPhase = ConversationPhase.EXPLORATION
    suggested_topics: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)


@dataclass
class SRAOutput(AgentOutput):
    """SRA agent specific output"""
    new_symptoms: List[Symptom] = field(default_factory=list)
    updated_symptoms: List[Symptom] = field(default_factory=list)
    criteria_matches: List[str] = field(default_factory=list)


@dataclass
class DiagnosisOutput(AgentOutput):
    """Diagnosis agent specific output"""
    primary: Optional[Dict] = None
    differentials: List[Dict] = field(default_factory=list)
    confidence: float = 0.0
    severity: Severity = Severity.MODERATE
    clinical_report: str = ""


__all__ = [
    # Enums
    "ResponseType", "Severity", "ConversationPhase", "RiskLevel", "ModuleStatus",
    # Core types
    "Symptom", "SCIDQuestion", "ProcessedResponse", "ConversationState",
    # Outputs
    "AgentOutput", "TherapistOutput", "SRAOutput", "DiagnosisOutput"
]
