"""
app/services/assessment_service.py
===================================
Service for managing AssessmentSession persistence and Agent orchestration.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.patient import AssessmentSession
from app.agents.state import MindMateState

logger = logging.getLogger(__name__)

class AssessmentService:
    @staticmethod
    def save_session_progress(session_id: str, state: MindMateState):
        """
        Saves current MindMateState results to the AssessmentSession.
        Handles both intermediate turn data and final clinical outputs.
        """
        db = SessionLocal()
        try:
            session = db.query(AssessmentSession).filter(AssessmentSession.session_id == session_id).first()
            if not session:
                logger.error(f"AssessmentSession {session_id} not found.")
                return

            # Intermediate interaction results
            report = state.get("clinical_report")
            if report:
                session.clinical_report = report
            
            summary = state.get("interview_summary")
            if summary:
                session.interview_summary = summary
                
            symptoms = state.get("symptoms")
            if symptoms:
                session.symptoms = [dict(s) for s in symptoms]
            
            is_completed = state.get("is_interview_complete")
            if is_completed is not None:
                session.is_completed = is_completed

            # Final clinical results (populated by DA nodes)
            diagnosis = state.get("diagnosis")
            if diagnosis:
                session.diagnoser_results = diagnosis.model_dump()
            
            plan = state.get("treatment_plan")
            if plan:
                session.treatment_plan = plan
                
            specialists = state.get("specialists")
            if specialists:
                session.recommended_specialists = specialists
            
            db.commit()
            logger.info(f"Saved session progress for ID {session_id}")
        except Exception as e:
            logger.error(f"Error saving session progress: {e}")
            db.rollback()
        finally:
            db.close()
