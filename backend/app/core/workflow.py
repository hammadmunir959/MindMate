"""
MindMate Workflow
=================
LangGraph-based workflow orchestrating all agents.
"""

from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime
import asyncio
import logging

from langgraph.graph import StateGraph, END

from app.agents.therapist import TherapistAgent
from app.agents.sra import SymptomRecognitionAgent
from app.agents.diagnosis import DiagnosisAgent
from app.agents.matcher import MatcherAgent


logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    """
    Shared state across all agents in the workflow.
    """
    # Session identity
    session_id: str
    patient_id: str
    started_at: str
    
    # User input
    user_message: str
    
    # Conversation data (Therapist Agent owns)
    messages: List[Dict]
    therapist_response: Optional[str]
    current_phase: str
    
    # Symptom data (SRA owns)
    symptoms: List[Dict]
    symptom_count: int
    
    # Diagnosis data (Diagnosis Agent owns)
    diagnosis: Optional[Dict]
    diagnosis_ready: bool
    
    # Matching data (Matcher Agent owns)
    matches: List[Dict]
    matching_complete: bool
    
    # Control flags
    requires_escalation: bool
    session_complete: bool
    error: Optional[str]


def create_initial_state(
    session_id: str,
    patient_id: str
) -> ConversationState:
    """Create initial state for a new session"""
    return ConversationState(
        session_id=session_id,
        patient_id=patient_id,
        started_at=datetime.utcnow().isoformat(),
        user_message="",
        messages=[],
        therapist_response=None,
        current_phase="rapport",
        symptoms=[],
        symptom_count=0,
        diagnosis=None,
        diagnosis_ready=False,
        matches=[],
        matching_complete=False,
        requires_escalation=False,
        session_complete=False,
        error=None,
    )


# Agent instances (initialized once)
_therapist_agent = None
_sra_agent = None
_diagnosis_agent = None
_matcher_agent = None


def _get_agents():
    """Get or initialize agent instances"""
    global _therapist_agent, _sra_agent, _diagnosis_agent, _matcher_agent
    
    if _therapist_agent is None:
        _therapist_agent = TherapistAgent()
    if _sra_agent is None:
        _sra_agent = SymptomRecognitionAgent()
    if _diagnosis_agent is None:
        _diagnosis_agent = DiagnosisAgent()
    if _matcher_agent is None:
        _matcher_agent = MatcherAgent()
    
    return _therapist_agent, _sra_agent, _diagnosis_agent, _matcher_agent


async def therapist_node(state: ConversationState) -> ConversationState:
    """
    Therapist agent node - generates response to user.
    """
    therapist, _, _, _ = _get_agents()
    
    try:
        result = await therapist.process(state)
        
        # Add user message to history
        if state["user_message"]:
            state["messages"].append({
                "role": "user",
                "content": state["user_message"],
                "timestamp": datetime.utcnow().isoformat(),
            })
        
        # Add therapist response to state
        state["therapist_response"] = result.content
        state["current_phase"] = result.metadata.get("phase", state["current_phase"])
        
        # Add therapist message to history
        state["messages"].append({
            "role": "assistant",
            "content": result.content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Check for escalation
        if result.metadata.get("requires_escalation"):
            state["requires_escalation"] = True
        
    except Exception as e:
        logger.error(f"Therapist node error: {e}")
        state["error"] = str(e)
    
    return state


async def sra_node(state: ConversationState) -> ConversationState:
    """
    SRA agent node - extracts symptoms asynchronously.
    This runs in parallel with the therapist response.
    """
    _, sra, _, _ = _get_agents()
    
    try:
        result = await sra.process(state)
        
        if result.success:
            state["symptoms"] = result.content
            state["symptom_count"] = result.metadata.get("total_symptoms", 0)
        
    except Exception as e:
        logger.error(f"SRA node error: {e}")
        # Don't set error - SRA failure shouldn't block conversation
    
    return state


async def diagnosis_node(state: ConversationState) -> ConversationState:
    """
    Diagnosis agent node - generates diagnosis from symptoms.
    """
    _, _, diagnosis_agent, _ = _get_agents()
    
    try:
        result = await diagnosis_agent.process(state)
        
        if result.success:
            state["diagnosis"] = result.content
            state["diagnosis_ready"] = True
        
    except Exception as e:
        logger.error(f"Diagnosis node error: {e}")
        state["error"] = str(e)
    
    return state


async def matcher_node(state: ConversationState) -> ConversationState:
    """
    Matcher agent node - finds specialist matches.
    """
    _, _, _, matcher = _get_agents()
    
    try:
        result = await matcher.process(state)
        
        if result.success:
            state["matches"] = result.content.get("matches", [])
            state["matching_complete"] = True
        
    except Exception as e:
        logger.error(f"Matcher node error: {e}")
        state["error"] = str(e)
    
    return state


def should_continue_chat(state: ConversationState) -> str:
    """
    Determine next step after therapist response.
    """
    # Check for high risk - immediate escalation
    if state.get("requires_escalation"):
        return "escalate"
    
    # Check if session is complete
    if state.get("session_complete"):
        return "complete"
    
    # Check if enough symptoms for diagnosis
    if should_trigger_diagnosis(state):
        return "diagnosis"
    
    # Continue conversation
    return "continue"


def should_trigger_diagnosis(state: ConversationState) -> bool:
    """
    Determine if we have enough data for diagnosis.
    """
    symptoms = state.get("symptoms", [])
    messages = state.get("messages", [])
    
    # Minimum thresholds
    min_symptoms = 3
    min_messages = 8
    
    has_enough_symptoms = len(symptoms) >= min_symptoms
    has_enough_conversation = len(messages) >= min_messages
    
    # Check for severity indicator
    has_severity = any(s.get("severity", 0) >= 0.6 for s in symptoms)
    
    return has_enough_symptoms and has_enough_conversation and has_severity


def create_mindmate_workflow():
    """
    Create the MindMate LangGraph workflow.
    
    Flow:
    1. Therapist generates response
    2. SRA extracts symptoms (async)
    3. If threshold met -> Diagnosis -> Matcher
    4. Otherwise -> back to Therapist
    """
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("therapist", therapist_node)
    workflow.add_node("sra", sra_node)
    workflow.add_node("diagnosis", diagnosis_node)
    workflow.add_node("matcher", matcher_node)
    
    # Entry point
    workflow.set_entry_point("therapist")
    
    # After therapist, always run SRA
    workflow.add_edge("therapist", "sra")
    
    # After SRA, decide next step
    workflow.add_conditional_edges(
        "sra",
        should_continue_chat,
        {
            "continue": END,  # Wait for next user message
            "diagnosis": "diagnosis",
            "escalate": END,
            "complete": "diagnosis",  # Generate final diagnosis on complete
        }
    )
    
    # Diagnosis flows to matcher
    workflow.add_edge("diagnosis", "matcher")
    
    # Matcher is terminal
    workflow.add_edge("matcher", END)
    
    return workflow.compile()


# Singleton workflow instance
_workflow = None


def get_workflow():
    """Get or create workflow instance"""
    global _workflow
    if _workflow is None:
        _workflow = create_mindmate_workflow()
    return _workflow


async def process_message(
    session_id: str,
    patient_id: str,
    message: str,
    current_state: Optional[ConversationState] = None
) -> ConversationState:
    """
    Process a user message through the workflow.
    
    Args:
        session_id: Session identifier
        patient_id: Patient identifier
        message: User message
        current_state: Current state (or None for new session)
    
    Returns:
        Updated state after processing
    """
    workflow = get_workflow()
    
    # Initialize or update state
    if current_state is None:
        state = create_initial_state(session_id, patient_id)
    else:
        state = current_state.copy()
    
    state["user_message"] = message
    
    # Run workflow
    result = await workflow.ainvoke(state)
    
    return result


__all__ = [
    "ConversationState",
    "create_initial_state",
    "create_mindmate_workflow",
    "get_workflow",
    "process_message",
]
