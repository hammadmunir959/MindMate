from typing import TypedDict, Annotated, Literal, Optional, List
from uuid import UUID
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# State Models (TypedDicts for LangGraph)
# ---------------------------------------------------------------------------

class SCIDCriterion(TypedDict):
    criterion_id: str
    module: str
    description: str
    status: Literal["met", "not_met", "uncertain", "pending"]
    evidence: str


class Symptom(TypedDict):
    name: str
    onset_offset_period: str
    severity: int  # 1-10
    frequency: str
    impact_on_functioning: str
    raw_evidence: str


class EscalationFlag(TypedDict):
    level: Literal["low", "medium", "high", "critical"]
    reason: str
    detected_at_turn: int


class SupervisorDecision(TypedDict):
    next_module: Literal[
        "SCID_SC", "MDD", "BIPOLAR", "GAD", "PTSD", "PANIC",
        "SOCIAL_ANXIETY", "OCD", "ADHD", "SUBSTANCE_USE", "EATING", "RISK", "COMPLETE"
    ]
    rationale: str
    escalation: Optional[EscalationFlag]
    confidence: float  # 0.0 – 1.0
    stay_in_module: bool


class PIAState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    turn_count: int
    active_module: str
    system_prompt: str
    patient_context: dict
    supervisor_decision: Optional[SupervisorDecision]
    modules_visited: list[str]
    scid_criteria: list[SCIDCriterion]
    symptoms: list[Symptom]
    escalation: Optional[EscalationFlag]
    is_interview_complete: bool
    interview_summary: Optional[str]
    clinical_report: Optional[str]
    diagnoser_results: Optional[dict] = None
    treatment_plan: Optional[str] = None
    recommended_specialists: Optional[list] = None


class DAState(TypedDict):
    """State for the Diagnoser Agent (DA) execution."""
    patient_id: Optional[int]
    patient_context: dict
    symptoms: list[Symptom]
    clinical_report: str
    interview_summary: str
    
    # Internal Node Outputs
    diagnosis: Optional["DiagnosisOutput"]
    treatment_plan: Optional[str]
    specialists: Optional[list[dict]]
    
    # Orchestration
    errors: list[str]


# ---------------------------------------------------------------------------
# Pydantic structured output models (used internally by nodes)
# ---------------------------------------------------------------------------

class SymptomItem(BaseModel):
    name: str = Field(description="Clinical symptom name, e.g. 'Insomnia'")
    onset_offset_period: str = Field(description="When it started/ended, or 'Not specified'")
    severity: int = Field(ge=1, le=10, description="Severity 1-10")
    frequency: str = Field(description="How often, e.g. 'Daily'")
    impact_on_functioning: str = Field(description="Impact on work/relationships")
    raw_evidence: str = Field(description="Verbatim patient quote(s)")


class ExtractedSymptoms(BaseModel):
    symptoms: list[SymptomItem] = Field(default_factory=list)


class EscalationOutput(BaseModel):
    level: Literal["low", "medium", "high", "critical"]
    reason: str
    detected_at_turn: int


class SupervisorOutput(BaseModel):
    next_module: Literal[
        "ONBOARDING", "SCID_SC", "MDD", "BIPOLAR", "GAD", "PTSD", "PANIC",
        "SOCIAL_ANXIETY", "OCD", "ADHD", "SUBSTANCE_USE", "EATING", "RISK", "COMPLETE"
    ]
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    stay_in_module: bool
    escalation: Optional[EscalationOutput] = None


# ---------------------------------------------------------------------------
# DA (Diagnoser Agent) Structured Output Models
# ---------------------------------------------------------------------------

class DiagnosisDetail(BaseModel):
    disorder: str = Field(description="Name of the DSM-5 disorder")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level")
    rationale: str = Field(description="Clinical rationale based on evidence")
    is_primary: bool = Field(default=False)

class DiagnosisOutput(BaseModel):
    differential_diagnoses: list[DiagnosisDetail]
    dsm5_code_estimates: list[str] = Field(description="Estimated ICD-10 or DSM-5 codes")

class TreatmentPlanOutput(BaseModel):
    plan_markdown: str = Field(description="Full non-medical treatment plan in markdown")
    key_interventions: list[str] = Field(description="3-5 critical therapeutic steps")

class SpecialistMatch(BaseModel):
    specialist_id: UUID
    name: str
    specialization: str
    location: str
    match_score: float
    reason: str

# ---------------------------------------------------------------------------
# API Request/Response Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # If None, a new session is created

class SessionResponse(BaseModel):
    session_id: str
    patient_id: UUID
