"""
app/agents/state.py
====================
Unified state model for the MindMate AI agentic system.
Integrates interaction, clinical screening, and diagnostic outputs.
"""

from typing import TypedDict, Annotated, Literal, Optional, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from app.schemas.agent_schemas import (
    SCIDCriterion, Symptom, EscalationFlag, SupervisorDecision,
    DiagnosisOutput, SpecialistMatch
)

class MindMateState(TypedDict):
    # Core Interaction
    messages: Annotated[list[BaseMessage], add_messages]
    turn_count: int
    active_module: str
    system_prompt: str
    
    # Context & Patient Info
    patient_id: Optional[int]
    patient_context: dict
    
    # Clinical Extraction (Mid-interview)
    modules_visited: list[str]
    scid_criteria: list[SCIDCriterion]
    symptoms: list[Symptom]
    escalation: Optional[EscalationFlag]
    interview_summary: Optional[str]
    clinical_report: Optional[str]
    
    # Control Flow
    supervisor_decision: Optional[SupervisorDecision]
    is_interview_complete: bool  # True when supervisor says COMPLETE
    
    # Final Clinical Outputs (Post-interview)
    diagnosis: Optional[DiagnosisOutput]
    treatment_plan: Optional[str]
    specialists: Optional[list[dict]] # List of SpecialistMatch serialized
    
    # Error handling
    errors: list[str]
