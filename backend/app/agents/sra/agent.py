"""
Symptom Recognition Agent (SRA)
===============================
Asynchronous background agent for continuous symptom extraction.
Runs on EVERY user message without blocking the conversation.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from app.agents.base import BaseAgent, AgentOutput
from app.agents.sra.extractors import SymptomExtractor
from app.agents.sra.symptom_db import DSM5SymptomDatabase


logger = logging.getLogger(__name__)


class SymptomRecognitionAgent(BaseAgent):
    """
    Symptom Recognition Agent (SRA)
    
    Key Features:
    - Runs asynchronously on every user message
    - Does NOT block the conversation flow
    - Continuously updates shared state with symptoms
    - Uses hybrid NER + LLM extraction
    - Stateless (DB-backed)
    """
    
    def __init__(self, llm_client=None, **kwargs):
        super().__init__(agent_name="SRAAgent", **kwargs)
        self.extractor = SymptomExtractor(llm_client)
        self.executor = ThreadPoolExecutor(max_workers=4)
        # Cache removed for stateless operation
    
    async def process(self, state: Dict) -> AgentOutput:
        """
        Process user message and extract symptoms.
        Database-backed execution.
        """
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            user_message = state.get("user_message", "")
            session_id = state.get("session_id")
            
            if not session_id or len(user_message.strip()) < 3:
                 return AgentOutput(content=[], metadata={"skipped": True})
            
            # DB Context for this execution
            db = SessionLocal()
            try:
                # 1. Fetch Context & Existing Symptoms (from DB)
                existing_symptoms_objs = assessment_repo.get_symptoms(db, session_id)
                
                # 2. Extract 
                new_symptoms = await self.extractor.extract(
                    text=user_message,
                    context="" # Context could be enhanced here by reading history
                )
                
                # 3. Upsert to DB
                processed_symptoms = []
                for symptom in new_symptoms:
                    # Enrich with severity if missing
                    if "severity" not in symptom:
                        symptom["severity"] = 0.5
                    
                    # Sanitize for DB (remove fields not in model)
                    
                    # Map category to Enum
                    category_map = {
                        "depressive_disorders": "depressive",
                        "depressive": "depressive",
                        "anxiety_disorders": "anxiety",
                        "anxiety": "anxiety",
                        "trauma_and_stressor_related_disorders": "trauma",
                        "trauma": "trauma",
                        "bipolar_and_related_disorders": "bipolar",
                        "bipolar": "bipolar",
                        "obsessive_compulsive_and_related_disorders": "ocd",
                        "ocd": "ocd",
                        "feeding_and_eating_disorders": "eating",
                        "eating": "eating",
                        "sleep_wake_disorders": "sleep",
                        "sleep": "sleep",
                        "substance_related_and_addictive_disorders": "substance",
                        "substance": "substance"
                    }
                    
                    raw_category = str(symptom.get("category", "")).lower()
                    mapped_category = category_map.get(raw_category, "other")
                    
                    db_symptom = {
                        "symptom_name": symptom.get("symptom_name") or symptom.get("name"),
                        "severity": symptom.get("severity"),
                        "category": mapped_category,
                        "confidence": symptom.get("confidence")
                    }
                        
                    # Save/Update in DB
                    saved = assessment_repo.upsert_symptom(db, session_id, db_symptom)
                    processed_symptoms.append(
                        {"name": saved.symptom_name, "severity": float(saved.severity)}
                    )
                
                if new_symptoms:
                    self.log_info(f"SRA: Extracted {len(new_symptoms)} symptoms for {session_id}")
                
                return AgentOutput(
                    content=processed_symptoms,
                    metadata={"count": len(processed_symptoms)}
                )
                
            finally:
                db.close()
                
        except Exception as e:
            self.log_error(f"SRA extraction failed: {e}", exc_info=True)
            return AgentOutput(content=[], error=str(e))

__all__ = ["SymptomRecognitionAgent"]
