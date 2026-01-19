"""
Diagnosis Agent (Agentic v2)
============================
Fully agentic DSM-5 compliant diagnostic analysis using MCP tools.
Uses decision tree algorithm: 3-5 steps instead of 14 brute-force calls.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentOutput
from app.agents.diagnosis.mcp_server import MCPToolServer

logger = logging.getLogger(__name__)


@dataclass
class Diagnosis:
    """Represents a diagnostic conclusion"""
    disorder_code: str
    disorder_name: str
    category: str
    confidence: float
    criteria_met: List[str]
    criteria_total: int
    severity: str
    is_primary: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "disorder_code": self.disorder_code,
            "disorder_name": self.disorder_name,
            "category": self.category,
            "confidence": self.confidence,
            "criteria_met": self.criteria_met,
            "criteria_total": self.criteria_total,
            "severity": self.severity,
            "is_primary": self.is_primary,
        }


class DiagnosisAgent(BaseAgent):
    """
    Agentic Diagnosis Agent with MCP Tool Server.
    
    Uses decision tree algorithm:
    1. Screen categories (1 LLM call)
    2. Get candidate disorders (deterministic)
    3. Evaluate criteria (1-2 LLM calls)
    4. Generate report (1 LLM call)
    
    Total: 3-5 LLM calls instead of 14
    """
    
    def __init__(self, llm_client=None, **kwargs):
        super().__init__(agent_name="DiagnosisAgent", **kwargs)
        self.llm_client = llm_client
        self.mcp_server = MCPToolServer(llm_client=llm_client)
    
    async def process(self, state: Dict) -> AgentOutput:
        """
        Run the agentic diagnosis loop.
        
        Uses ReAct pattern:
        - Observe: Fetch symptoms
        - Think/Act: Use MCP tools in sequence
        - Return: Final diagnosis report
        """
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            session_id = state.get("session_id")
            patient_id = state.get("patient_id")
            
            if not session_id or not patient_id:
                return AgentOutput(
                    content={"error": "Missing session_id or patient_id"},
                    error="Missing context"
                )
            
            db = SessionLocal()
            try:
                # ============ STEP 0: OBSERVE ============
                self.log_info(f"[OBSERVE] Fetching symptoms for session {session_id}")
                
                symptoms_objs = assessment_repo.get_symptoms(db, session_id)
                symptoms = [
                    {
                        "name": s.symptom_name,
                        "severity": float(s.severity),
                        "category": s.category,
                        "confidence": float(s.confidence or 0.8)
                    }
                    for s in symptoms_objs
                ]
                
                if len(symptoms) < 2:
                    return AgentOutput(
                        content={
                            "diagnoses": [],
                            "message": "Insufficient symptoms for diagnosis"
                        },
                        metadata={"status": "insufficient_data"}
                    )
                
                self.log_info(f"[OBSERVE] Found {len(symptoms)} symptoms")
                
                # ============ STEP 1: SCREEN CATEGORIES ============
                self.log_info("[ACT] Tool: screen_categories")
                
                screen_result = await self.mcp_server.call_tool(
                    "screen_categories",
                    {"symptoms": symptoms}
                )
                
                categories = screen_result.get("categories", ["mood_disorders"])
                self.log_info(f"[RESULT] Categories: {categories}")
                
                # ============ STEP 2: GET CANDIDATES ============
                self.log_info("[ACT] Tool: get_candidate_disorders")
                
                candidates_result = await self.mcp_server.call_tool(
                    "get_candidate_disorders",
                    {"categories": categories, "symptoms": symptoms}
                )
                
                candidates = candidates_result.get("candidates", [])
                self.log_info(f"[RESULT] Candidates: {candidates} (filtered from {candidates_result.get('total_in_categories', 0)})")
                
                if not candidates:
                    # Fallback: Try mood disorders if no candidates
                    candidates = ["MDD"]
                
                # ============ STEP 3: EVALUATE EACH CANDIDATE ============
                confirmed_diagnoses = []
                
                for disorder_id in candidates[:3]:  # Limit to top 3 candidates
                    self.log_info(f"[ACT] Tool: evaluate_criteria for {disorder_id}")
                    
                    eval_result = await self.mcp_server.call_tool(
                        "evaluate_criteria",
                        {"disorder_id": disorder_id, "symptoms": symptoms}
                    )
                    
                    if eval_result.get("criteria_met"):
                        self.log_info(f"[RESULT] {disorder_id}: CONFIRMED ({eval_result.get('met_count')}/{eval_result.get('required_count')} criteria)")
                        confirmed_diagnoses.append(eval_result)
                    else:
                        self.log_info(f"[RESULT] {disorder_id}: Not met ({eval_result.get('met_count')}/{eval_result.get('required_count')} criteria)")
                
                # ============ STEP 4: GENERATE REPORT ============
                self.log_info("[ACT] Tool: generate_report")
                
                report_result = await self.mcp_server.call_tool(
                    "generate_report",
                    {"diagnoses": confirmed_diagnoses, "symptoms": symptoms}
                )
                
                self.log_info(f"[COMPLETE] Generated report with {len(confirmed_diagnoses)} diagnoses")
                
                # ============ SAVE TO DATABASE ============
                # Map categories to database enum values
                CATEGORY_MAP = {
                    "mood_disorders": "depressive",
                    "anxiety_disorders": "anxiety",
                    "trauma_stressor_disorders": "trauma",
                    "substance_use_disorders": "substance",
                    "neurodevelopmental_disorders": "other",
                    "obsessive_compulsive_disorders": "ocd",
                    "feeding_eating_disorders": "eating",
                    "sleep_wake_disorders": "sleep"
                }
                
                for diag in confirmed_diagnoses:
                    raw_category = diag.get("category", "")
                    mapped_category = CATEGORY_MAP.get(raw_category, "other")
                    
                    db_data = {
                        "disorder_code": diag.get("disorder_id", ""),
                        "disorder_name": diag.get("disorder_name", ""),
                        "category": mapped_category,
                        "confidence": diag.get("confidence", 0),
                        "severity": diag.get("severity", "moderate"),
                        "criteria_met": diag.get("met_criteria_ids", []),
                        "criteria_total": diag.get("total_criteria", 0),
                        "is_primary": diag.get("is_primary", False),
                        "clinical_report": report_result.get("report") if diag.get("is_primary") else None
                    }
                    assessment_repo.add_diagnosis(db, session_id, patient_id, db_data)
                
                return AgentOutput(
                    content={
                        "diagnoses": confirmed_diagnoses,
                        "primary_diagnosis": report_result.get("primary_diagnosis"),
                        "clinical_report": report_result.get("report"),
                        "recommendations": report_result.get("recommendations", []),
                        "steps_taken": 4,
                        "total_llm_calls": 2 + len([d for d in candidates[:3] if True])  # estimate
                    },
                    metadata={
                        "diagnosis_count": len(confirmed_diagnoses),
                        "categories_screened": categories,
                        "candidates_evaluated": candidates[:3],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
            finally:
                db.close()
                
        except Exception as e:
            self.log_error(f"Diagnosis failed: {e}", exc_info=True)
            return AgentOutput(
                content={"diagnoses": [], "error": str(e)},
                error=str(e)
            )


__all__ = ["DiagnosisAgent", "Diagnosis"]
