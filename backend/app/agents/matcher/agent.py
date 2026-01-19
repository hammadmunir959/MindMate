"""
Matcher Agent
=============
Matches diagnosed patients with appropriate mental health specialists.
Uses database for specialists and persists matches.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.agents.base import BaseAgent, AgentOutput


# Category mapping: Diagnosis category -> Specialist specializations
CATEGORY_TO_SPECIALIZATION = {
    "depressive": ["depression", "mood_disorders"],
    "anxiety": ["anxiety", "stress"],
    "trauma": ["trauma_ptsd", "crisis"],
    "bipolar": ["bipolar", "mood_disorders"],
    "ocd": ["ocd", "anxiety"],
    "eating": ["eating_disorders"],
    "sleep": ["sleep", "behavioral"],
    "substance": ["addiction", "substance_abuse"],
    "other": []  # Match all specialists
}

# Scoring weights
WEIGHT_CATEGORY = 0.40
WEIGHT_RATING = 0.25
WEIGHT_AVAILABILITY = 0.20
WEIGHT_EXPERIENCE = 0.15


@dataclass
class SpecialistScore:
    """Represents a scored specialist match"""
    specialist_id: str
    specialist_name: str
    score: float
    rank: int
    reasons: List[str]
    specializations: List[str]
    rating: float
    experience_years: int
    fee: float
    
    def to_dict(self) -> Dict:
        return {
            "specialist_id": self.specialist_id,
            "specialist_name": self.specialist_name,
            "score": self.score,
            "rank": self.rank,
            "reasons": self.reasons,
            "specializations": self.specializations,
            "rating": self.rating,
            "experience_years": self.experience_years,
            "fee": float(self.fee) if self.fee else None
        }


class MatcherAgent(BaseAgent):
    """
    Matcher Agent for specialist-patient matching.
    
    Uses weighted scoring based on:
    - Category match (40%)
    - Rating (25%)
    - Availability (20%)
    - Experience (15%)
    """
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="MatcherAgent", **kwargs)
        self.top_n = 5  # Number of matches to return
    
    async def process(self, state: Dict) -> AgentOutput:
        """
        Match patient to specialists based on diagnosis.
        
        Args:
            state: Contains session_id, patient_id, diagnosis (optional)
        """
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            from app.db.repositories_new.specialist import specialist_repo
            
            session_id = state.get("session_id")
            patient_id = state.get("patient_id")
            
            if not session_id or not patient_id:
                return AgentOutput(
                    content={"error": "Missing session_id or patient_id"},
                    error="Missing context"
                )
            
            db = SessionLocal()
            try:
                # 1. Fetch diagnosis for session
                diagnoses = assessment_repo.get_diagnoses(db, session_id)
                
                if not diagnoses:
                    return AgentOutput(
                        content={
                            "matches": [],
                            "message": "No diagnosis found. Complete assessment first."
                        },
                        metadata={"status": "no_diagnosis"}
                    )
                
                # Get primary diagnosis
                primary_diag = next(
                    (d for d in diagnoses if d.is_primary), 
                    diagnoses[0]
                )
                diagnosis_category = primary_diag.category or "other"
                
                # 2. Fetch approved specialists
                specialists = specialist_repo.get_approved(db, limit=50)
                
                if not specialists:
                    return AgentOutput(
                        content={
                            "matches": [],
                            "message": "No specialists available at this time."
                        },
                        metadata={"status": "no_specialists"}
                    )
                
                # 3. Score each specialist
                scored = []
                target_specs = CATEGORY_TO_SPECIALIZATION.get(
                    diagnosis_category, []
                )
                
                for spec in specialists:
                    score, reasons = self._score_specialist(
                        specialist=spec,
                        target_specializations=target_specs,
                        diagnosis_category=diagnosis_category
                    )
                    
                    scored.append(SpecialistScore(
                        specialist_id=str(spec.id),
                        specialist_name=spec.full_name,
                        score=round(score, 2),
                        rank=0,  # Set after sorting
                        reasons=reasons,
                        specializations=spec.specializations or [],
                        rating=float(spec.average_rating or 0),
                        experience_years=spec.experience_years or 0,
                        fee=spec.fee_per_session
                    ))
                
                # 4. Sort and rank
                scored.sort(key=lambda x: x.score, reverse=True)
                top_matches = scored[:self.top_n]
                
                for i, match in enumerate(top_matches):
                    match.rank = i + 1
                
                # 5. Persist matches to DB
                for match in top_matches:
                    assessment_repo.add_specialist_match(
                        db=db,
                        session_id=session_id,
                        specialist_id=match.specialist_id,
                        match_data={
                            "match_score": match.score,
                            "rank": match.rank,
                            "match_reasons": match.reasons
                        }
                    )
                
                self.log_info(
                    f"Matched {len(top_matches)} specialists for session {session_id}"
                )
                
                return AgentOutput(
                    content={
                        "matches": [m.to_dict() for m in top_matches],
                        "diagnosis_category": diagnosis_category,
                        "total_evaluated": len(specialists)
                    },
                    metadata={
                        "match_count": len(top_matches),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
            finally:
                db.close()
                
        except Exception as e:
            self.log_error(f"Matching failed: {e}", exc_info=True)
            return AgentOutput(
                content={"matches": [], "error": str(e)},
                error=str(e)
            )
    
    def _score_specialist(
        self,
        specialist,
        target_specializations: List[str],
        diagnosis_category: str
    ) -> tuple[float, List[str]]:
        """
        Score a specialist based on weighted criteria.
        
        Returns: (score, list of reasons)
        """
        score = 0.0
        reasons = []
        
        # 1. Category Match (40%)
        spec_specializations = [s.lower() for s in (specialist.specializations or [])]
        
        if not target_specializations:
            # "other" category - give partial credit to all
            category_score = 0.5
            reasons.append("General mental health specialist")
        else:
            matches = [
                t for t in target_specializations 
                if t.lower() in spec_specializations
            ]
            if matches:
                category_score = 1.0
                reasons.append(f"Specializes in {', '.join(matches)}")
            else:
                category_score = 0.2
                reasons.append("Related experience")
        
        score += category_score * WEIGHT_CATEGORY
        
        # 2. Rating (25%)
        rating = float(specialist.average_rating or 0)
        rating_score = rating / 5.0  # Normalize to 0-1
        score += rating_score * WEIGHT_RATING
        
        if rating >= 4.5:
            reasons.append(f"Highly rated ({rating:.1f}/5)")
        elif rating >= 4.0:
            reasons.append(f"Well rated ({rating:.1f}/5)")
        
        # 3. Availability (20%)
        schedule = specialist.weekly_schedule or {}
        if schedule:
            has_slots = any(
                len(slots) > 0 
                for slots in schedule.values() 
                if isinstance(slots, list)
            )
            availability_score = 1.0 if has_slots else 0.3
            if has_slots:
                reasons.append("Has available slots")
        else:
            availability_score = 0.5  # Unknown availability
        
        score += availability_score * WEIGHT_AVAILABILITY
        
        # 4. Experience (15%)
        years = specialist.experience_years or 0
        experience_score = min(1.0, years / 15.0)  # Max out at 15 years
        score += experience_score * WEIGHT_EXPERIENCE
        
        if years >= 10:
            reasons.append(f"{years}+ years experience")
        elif years >= 5:
            reasons.append(f"{years} years experience")
        
        return score, reasons


__all__ = ["MatcherAgent", "SpecialistScore"]
