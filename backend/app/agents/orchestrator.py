"""
Conversation Orchestrator
=========================
Routes messages between agents following the architecture design.
"""

from typing import Dict, Any, Optional
import asyncio
import logging

from app.agents.core import (
    ConversationState, ConversationPhase, RiskLevel,
    get_state_manager, get_registry, AgentOutput
)
from app.agents.therapist.agent_v2 import TherapistAgentV2
from app.agents.sra.agent_v2 import SRAAgentV2
from app.agents.diagnosis.agent_v2 import DiagnosisAgentV2

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """
    Central orchestrator for the conversation flow.
    
    Architecture:
    - User message → Therapist (SYNC) + SRA (ASYNC parallel)
    - Therapist response returned to user
    - SRA updates state in background
    - When sufficient data → Diagnosis triggered
    
    Following system design:
    - Event-driven modular monolith
    - Shared state store
    - Agent orchestration
    """
    
    def __init__(self):
        self.therapist = TherapistAgentV2()
        self.sra = SRAAgentV2()
        self.diagnosis = DiagnosisAgentV2()
        self.state_manager = get_state_manager()
    
    async def process_message(
        self,
        session_id: str,
        patient_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent pipeline.
        
        Returns:
            {
                "response": str (therapist response),
                "phase": str,
                "symptom_count": int,
                "diagnosis_ready": bool
            }
        """
        
        # Get or create state
        state = self.state_manager.get_or_create(session_id, patient_id)
        
        # Prepare input
        agent_input = {
            "session_id": session_id,
            "patient_id": patient_id,
            "user_message": user_message
        }
        
        # Run Therapist (SYNC) and SRA (ASYNC) in parallel
        therapist_task = self.therapist.process(agent_input)
        sra_task = self.sra.process(agent_input)
        
        # Therapist is prioritized - we need its response
        therapist_result = await therapist_task
        
        # SRA runs in background - don't wait for it
        asyncio.create_task(self._run_sra_background(sra_task))
        
        # Update state after therapist
        state = self.state_manager.get(session_id)
        
        # Check if diagnosis should be triggered
        diagnosis_triggered = False
        diagnosis_result = None
        
        if state and state.should_trigger_diagnosis() and not state.diagnosis_ready:
            try:
                diagnosis_result = await self.diagnosis.process(agent_input)
                diagnosis_triggered = True
                logger.info(f"Diagnosis triggered for session {session_id}")
            except Exception as e:
                logger.error(f"Diagnosis failed: {e}")
        
        return {
            "response": therapist_result.content,
            "phase": therapist_result.metadata.get("phase", "exploration"),
            "symptom_count": therapist_result.metadata.get("symptom_count", 0),
            "risk_level": therapist_result.metadata.get("risk_level", "none"),
            "message_count": therapist_result.metadata.get("message_count", 0),
            "diagnosis_ready": state.diagnosis_ready if state else False,
            "diagnosis_triggered": diagnosis_triggered,
            "diagnosis": diagnosis_result.content if diagnosis_result else None
        }
    
    async def _run_sra_background(self, sra_task):
        """Run SRA in background without blocking"""
        try:
            result = await sra_task
            if result.metadata.get("count", 0) > 0:
                logger.debug(f"SRA extracted {result.metadata['count']} symptoms")
        except Exception as e:
            logger.warning(f"SRA background task failed: {e}")
    
    async def start_session(
        self,
        session_id: str,
        patient_id: str
    ) -> Dict[str, Any]:
        """Start a new conversation session"""
        
        # Create state
        state = self.state_manager.get_or_create(session_id, patient_id)
        
        # Get greeting from therapist
        agent_input = {
            "session_id": session_id,
            "patient_id": patient_id,
            "user_message": ""
        }
        
        result = await self.therapist.process(agent_input)
        
        return {
            "response": result.content,
            "session_id": session_id,
            "phase": "rapport"
        }
    
    async def get_diagnosis(self, session_id: str) -> Optional[Dict]:
        """Get diagnosis for a session"""
        
        state = self.state_manager.get(session_id)
        if not state:
            return None
        
        if state.diagnosis_ready and state.primary_diagnosis:
            return {
                "primary": state.primary_diagnosis,
                "differentials": state.differential_diagnoses,
                "symptom_count": len(state.symptoms)
            }
        
        # Run diagnosis
        result = await self.diagnosis.process({
            "session_id": session_id,
            "patient_id": state.patient_id
        })
        
        return result.content if result else None
    
    def get_session_state(self, session_id: str) -> Optional[Dict]:
        """Get current session state"""
        state = self.state_manager.get(session_id)
        if not state:
            return None
        
        return {
            "session_id": state.session_id,
            "patient_id": state.patient_id,
            "phase": state.phase.value,
            "message_count": len(state.messages),
            "symptom_count": len(state.symptoms),
            "symptoms": [
                {"name": s.name, "severity": s.severity, "category": s.category}
                for s in state.symptoms
            ],
            "diagnosis_ready": state.diagnosis_ready,
            "risk_level": state.risk_level.value
        }


# Singleton
_orchestrator: Optional[ConversationOrchestrator] = None


def get_orchestrator() -> ConversationOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ConversationOrchestrator()
    return _orchestrator


__all__ = ["ConversationOrchestrator", "get_orchestrator"]
