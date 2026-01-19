"""
Assessment Repository
=====================
Data access for multi-agent assessment workflow.
"""

from typing import Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.repositories_new.base import BaseRepository
from app.models_new.assessment import (
    AssessmentSession, ConversationMessage, ExtractedSymptom, Diagnosis, SessionStatus
)


class AssessmentRepository(BaseRepository[AssessmentSession, dict, dict]):
    """
    Repository for Assessment Sessions and related data.
    """
    
    def get_active_session(self, db: Session, patient_id: str) -> Optional[AssessmentSession]:
        """Get current active session for patient"""
        return db.query(AssessmentSession).filter(
            AssessmentSession.patient_id == patient_id,
            AssessmentSession.status == SessionStatus.ACTIVE
        ).first()
        
    def get_patient_history(
        self, db: Session, patient_id: str, limit: int = 10
    ) -> List[AssessmentSession]:
        """Get past sessions for patient"""
        return db.query(AssessmentSession).filter(
            AssessmentSession.patient_id == patient_id
        ).order_by(desc(AssessmentSession.started_at)).limit(limit).all()

    def add_message(
        self, db: Session, session_id: str, role: str, content: str, metadata: dict = None
    ) -> ConversationMessage:
        """Add a message to the conversation"""
        msg = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content,
            msg_metadata=metadata or {}
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        
        # Update message count on session
        session = self.get(db, session_id)
        if session:
            session.message_count += 1
            session.last_active_at = msg.created_at
            db.add(session)
            db.commit()
            
        return msg

    def get_conversation_history(
        self, db: Session, session_id: str
    ) -> List[ConversationMessage]:
        """Get full conversation history"""
        return db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.created_at).all()
    
    def add_symptom(
        self, db: Session, session_id: str, symptom_data: dict
    ) -> ExtractedSymptom:
        """Add an extracted symptom"""
        symptom = ExtractedSymptom(session_id=session_id, **symptom_data)
        db.add(symptom)
        db.commit()
        db.refresh(symptom)
        
        # Update symptom count
        session = self.get(db, session_id)
        if session:
            session.symptom_count += 1
            db.add(session)
            db.commit()
            
        return symptom
    
    def add_diagnosis(
        self, db: Session, session_id: str, patient_id: str, diagnosis_data: dict
    ) -> Diagnosis:
        """Add a diagnosis result"""
        diagnosis = Diagnosis(
            session_id=session_id, 
            patient_id=patient_id,
            **diagnosis_data
        )
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        return diagnosis


    def get_symptoms(self, db: Session, session_id: str) -> List[ExtractedSymptom]:
        """Get all symptoms for a session"""
        return db.query(ExtractedSymptom).filter(
            ExtractedSymptom.session_id == session_id
        ).all()

    def upsert_symptom(
        self, db: Session, session_id: str, symptom_data: dict
    ) -> ExtractedSymptom:
        """Update existing symptom or create new one"""
        symptom_name = symptom_data.get("symptom_name") or symptom_data.get("name")
        if not symptom_name:
            raise ValueError("Symptom name required")
            
        # Check existing
        existing = db.query(ExtractedSymptom).filter(
            ExtractedSymptom.session_id == session_id,
            ExtractedSymptom.symptom_name == symptom_name
        ).first()
        
        if existing:
            # Update fields
            for key, value in symptom_data.items():
                if key != "session_id" and hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            
            # Increment mention count
            existing.mention_count += 1
            existing.last_mentioned = symptom_data.get("last_mentioned") # Update timestamp
            
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new
            # Map 'name' to 'symptom_name' if needed
            data = symptom_data.copy()
            if "name" in data:
                data["symptom_name"] = data.pop("name")
                
            return self.add_symptom(db, session_id, data)

    def get_diagnoses(self, db: Session, session_id: str) -> List[Diagnosis]:
        """Get all diagnoses for a session"""
        return db.query(Diagnosis).filter(
            Diagnosis.session_id == session_id
        ).order_by(desc(Diagnosis.confidence)).all()

    def add_specialist_match(
        self, db: Session, session_id: str, specialist_id: str, match_data: dict
    ):
        """Add a specialist match for a session"""
        from app.models_new.specialist import SpecialistMatch
        
        # Check if match already exists
        existing = db.query(SpecialistMatch).filter(
            SpecialistMatch.session_id == session_id,
            SpecialistMatch.specialist_id == specialist_id
        ).first()
        
        if existing:
            # Update existing match
            existing.match_score = match_data.get("match_score", existing.match_score)
            existing.rank = match_data.get("rank", existing.rank)
            existing.match_reasons = match_data.get("match_reasons", existing.match_reasons)
            db.commit()
            return existing
        
        # Create new match
        match = SpecialistMatch(
            session_id=session_id,
            specialist_id=specialist_id,
            match_score=match_data.get("match_score", 0),
            rank=match_data.get("rank", 0),
            match_reasons=match_data.get("match_reasons", [])
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    def get_matches(self, db: Session, session_id: str):
        """Get all specialist matches for a session"""
        from app.models_new.specialist import SpecialistMatch
        
        return db.query(SpecialistMatch).filter(
            SpecialistMatch.session_id == session_id
        ).order_by(SpecialistMatch.rank).all()


assessment_repo = AssessmentRepository(AssessmentSession)
