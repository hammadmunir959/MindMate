"""
Patient Repository
==================
Data access for Patients.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.repositories_new.base import BaseRepository
from app.models_new.patient import Patient


class PatientRepository(BaseRepository[Patient, dict, dict]):
    """
    Repository for Patient operations.
    """
    
    def get_by_user_id(self, db: Session, user_id: str) -> Optional[Patient]:
        """Get patient by linked user ID"""
        return db.query(Patient).filter(Patient.user_id == user_id).first()
    
    def search(self, db: Session, query: str) -> List[Patient]:
        """Search patients by name"""
        search_filter = or_(
            Patient.first_name.ilike(f"%{query}%"),
            Patient.last_name.ilike(f"%{query}%")
        )
        return db.query(Patient).filter(search_filter).all()


patient_repo = PatientRepository(Patient)
