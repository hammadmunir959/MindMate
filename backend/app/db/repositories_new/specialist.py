"""
Specialist Repository
=====================
Data access for Specialists and Documents.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.repositories_new.base import BaseRepository
from app.models_new.specialist import Specialist, SpecialistDocument, ApprovalStatus


class SpecialistRepository(BaseRepository[Specialist, dict, dict]):
    """
    Repository for Specialist operations.
    """
    
    def get_by_user_id(self, db: Session, user_id: str) -> Optional[Specialist]:
        """Get specialist by linked user ID"""
        return db.query(Specialist).filter(Specialist.user_id == user_id).first()
    
    def get_approved(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Specialist]:
        """Get only approved specialists"""
        return db.query(Specialist).filter(
            Specialist.approval_status == ApprovalStatus.APPROVED
        ).offset(skip).limit(limit).all()
    
    def search(
        self, db: Session, query: str, city: Optional[str] = None
    ) -> List[Specialist]:
        """Search specialists by name, specialization, or city"""
        filters = []
        if query:
            filters.append(or_(
                Specialist.first_name.ilike(f"%{query}%"),
                Specialist.last_name.ilike(f"%{query}%"),
                Specialist.specializations.any(query)
            ))
        
        if city:
            filters.append(Specialist.city.ilike(f"%{city}%"))
            
        return db.query(Specialist).filter(
            Specialist.approval_status == ApprovalStatus.APPROVED,
            *filters
        ).all()


class SpecialistDocumentRepository(BaseRepository[SpecialistDocument, dict, dict]):
    """Repository for specialist documents"""
    pass


specialist_repo = SpecialistRepository(Specialist)
document_repo = SpecialistDocumentRepository(SpecialistDocument)
