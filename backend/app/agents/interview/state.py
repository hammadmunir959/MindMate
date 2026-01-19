"""
Interview State Manager
========================
Manages interview state including current module, progress, and adaptive flow.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class InterviewPhase(Enum):
    """Interview phases following SCID structure"""
    OVERVIEW = "overview"           # Initial open-ended exploration
    SCREENING = "screening"         # SCID-SC screening items
    DEEP_DIVE = "deep_dive"         # SCID-CV module deployment
    TIMELINE = "timeline"           # Duration, frequency assessment
    SUMMARY = "summary"             # Summarize and clarify


@dataclass
class InterviewState:
    """Complete interview state for a session"""
    session_id: str
    patient_id: str
    phase: InterviewPhase = InterviewPhase.OVERVIEW
    
    # Demographics (collected from patient profile or initial questions)
    demographics: Dict[str, Any] = field(default_factory=dict)
    
    # Screening results
    positive_screens: List[str] = field(default_factory=list)  # Module IDs with positive screens
    negative_screens: List[str] = field(default_factory=list)  # Module IDs ruled out
    screening_scores: Dict[str, float] = field(default_factory=dict)  # item_id -> score
    
    # Module deployment tracking
    deployed_modules: List[str] = field(default_factory=list)  # SCID-CV modules completed
    current_module: Optional[str] = None  # Currently active module ID
    module_progress: Dict[str, int] = field(default_factory=dict)  # module_id -> question_index
    
    # Question tracking
    asked_questions: List[str] = field(default_factory=list)  # Question IDs asked
    skipped_items: List[str] = field(default_factory=list)    # Question IDs skipped via logic
    current_question_id: Optional[str] = None
    
    # Adaptive flow
    priority_modules: List[str] = field(default_factory=list)  # Modules to deploy based on screening
    
    # Timestamps
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "patient_id": self.patient_id,
            "phase": self.phase.value,
            "demographics": self.demographics,
            "positive_screens": self.positive_screens,
            "negative_screens": self.negative_screens,
            "screening_scores": self.screening_scores,
            "deployed_modules": self.deployed_modules,
            "current_module": self.current_module,
            "module_progress": self.module_progress,
            "asked_questions": self.asked_questions,
            "skipped_items": self.skipped_items,
            "current_question_id": self.current_question_id,
            "priority_modules": self.priority_modules,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterviewState":
        state = cls(
            session_id=data.get("session_id", ""),
            patient_id=data.get("patient_id", "")
        )
        state.phase = InterviewPhase(data.get("phase", "overview"))
        state.demographics = data.get("demographics", {})
        state.positive_screens = data.get("positive_screens", [])
        state.negative_screens = data.get("negative_screens", [])
        state.screening_scores = data.get("screening_scores", {})
        state.deployed_modules = data.get("deployed_modules", [])
        state.current_module = data.get("current_module")
        state.module_progress = data.get("module_progress", {})
        state.asked_questions = data.get("asked_questions", [])
        state.skipped_items = data.get("skipped_items", [])
        state.current_question_id = data.get("current_question_id")
        state.priority_modules = data.get("priority_modules", [])
        return state


class InterviewStateManager:
    """Manages interview state persistence and retrieval"""
    
    def __init__(self):
        self._states: Dict[str, InterviewState] = {}  # In-memory cache
    
    def get_or_create(self, session_id: str, patient_id: str) -> InterviewState:
        """Get existing state or create new one"""
        if session_id not in self._states:
            # Try loading from DB first
            state = self._load_from_db(session_id)
            if not state:
                state = InterviewState(
                    session_id=session_id,
                    patient_id=patient_id,
                    started_at=datetime.utcnow()
                )
            self._states[session_id] = state
        
        return self._states[session_id]
    
    def save(self, state: InterviewState):
        """Save state to cache and DB"""
        state.last_activity = datetime.utcnow()
        self._states[state.session_id] = state
        self._save_to_db(state)
    
    def _load_from_db(self, session_id: str) -> Optional[InterviewState]:
        """Load state from database"""
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            db = SessionLocal()
            try:
                session = assessment_repo.get(db, session_id)
                if session and session.metadata:
                    interview_data = session.metadata.get("interview_state")
                    if interview_data:
                        return InterviewState.from_dict(interview_data)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not load interview state: {e}")
        return None
    
    def _save_to_db(self, state: InterviewState):
        """Save state to database"""
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            db = SessionLocal()
            try:
                session = assessment_repo.get(db, state.session_id)
                if session:
                    metadata = session.metadata or {}
                    metadata["interview_state"] = state.to_dict()
                    session.metadata = metadata
                    db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not save interview state: {e}")


# Singleton instance
state_manager = InterviewStateManager()


__all__ = ["InterviewPhase", "InterviewState", "InterviewStateManager", "state_manager"]
