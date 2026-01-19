"""
State Manager
=============
Session state management with persistence.
"""

from typing import Dict, Optional
from datetime import datetime
import logging

from app.agents.core.types import ConversationState

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages conversation state across agents.
    Provides in-memory caching with optional DB persistence.
    """
    
    def __init__(self):
        self._states: Dict[str, ConversationState] = {}
    
    def get(self, session_id: str) -> Optional[ConversationState]:
        """Get state for a session"""
        # Try cache first
        if session_id in self._states:
            return self._states[session_id]
        
        # Try loading from DB
        state = self._load_from_db(session_id)
        if state:
            self._states[session_id] = state
        return state
    
    def get_or_create(self, session_id: str, patient_id: str) -> ConversationState:
        """Get existing state or create new one"""
        state = self.get(session_id)
        if not state:
            state = ConversationState(
                session_id=session_id,
                patient_id=patient_id
            )
            self._states[session_id] = state
        return state
    
    def save(self, state: ConversationState):
        """Save state to cache and DB"""
        self._states[state.session_id] = state
        self._save_to_db(state)
    
    def delete(self, session_id: str):
        """Delete a session state"""
        if session_id in self._states:
            del self._states[session_id]
    
    def _load_from_db(self, session_id: str) -> Optional[ConversationState]:
        """Load state from database"""
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            db = SessionLocal()
            try:
                session = assessment_repo.get_session(db, session_id)
                if session and session.metadata:
                    data = session.metadata.get("conversation_state")
                    if data:
                        # Reconstruct ConversationState from dict
                        return self._dict_to_state(data)
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"Could not load state from DB: {e}")
        return None
    
    def _save_to_db(self, state: ConversationState):
        """Save state to database"""
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            db = SessionLocal()
            try:
                session = assessment_repo.get_session(db, state.session_id)
                if session:
                    metadata = session.metadata or {}
                    metadata["conversation_state"] = self._state_to_dict(state)
                    session.metadata = metadata
                    db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"Could not save state to DB: {e}")
    
    def _state_to_dict(self, state: ConversationState) -> Dict:
        """Convert state to serializable dict"""
        return {
            "session_id": state.session_id,
            "patient_id": state.patient_id,
            "phase": state.phase.value,
            "messages": state.messages[-20:],  # Keep last 20 messages
            "active_topics": state.active_topics,
            "symptoms": [
                {
                    "name": s.name,
                    "severity": s.severity,
                    "category": s.category,
                    "dsm_criteria_id": s.dsm_criteria_id
                }
                for s in state.symptoms
            ],
            "questions_asked": state.questions_asked,
            "modules_triggered": state.modules_triggered,
            "risk_level": state.risk_level.value,
            "diagnosis_ready": state.diagnosis_ready
        }
    
    def _dict_to_state(self, data: Dict) -> ConversationState:
        """Reconstruct state from dict"""
        from app.agents.core.types import Symptom, ConversationPhase, RiskLevel
        
        state = ConversationState(
            session_id=data.get("session_id", ""),
            patient_id=data.get("patient_id", "")
        )
        state.phase = ConversationPhase(data.get("phase", "exploration"))
        state.messages = data.get("messages", [])
        state.active_topics = data.get("active_topics", [])
        state.symptoms = [
            Symptom(
                name=s.get("name", ""),
                severity=s.get("severity", 0.5),
                category=s.get("category", ""),
                dsm_criteria_id=s.get("dsm_criteria_id")
            )
            for s in data.get("symptoms", [])
        ]
        state.questions_asked = data.get("questions_asked", [])
        state.modules_triggered = data.get("modules_triggered", [])
        state.risk_level = RiskLevel(data.get("risk_level", "none"))
        state.diagnosis_ready = data.get("diagnosis_ready", False)
        return state


# Singleton
_state_manager = StateManager()


def get_state_manager() -> StateManager:
    return _state_manager


__all__ = ["StateManager", "get_state_manager"]
