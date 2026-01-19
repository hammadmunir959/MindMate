"""
Optimized Diagnosis Agent V2
============================
DSM-5 compliant diagnosis with MCP tools.
Uses decision tree algorithm for efficiency.
"""

from typing import Dict, List, Any, Optional
import logging

from app.agents.base import BaseAgent, AgentOutput
from app.agents.core import (
    Symptom, Severity, ConversationState,
    get_state_manager, get_registry, register_tool
)
from app.core.llm_client import AgentLLMClient

logger = logging.getLogger(__name__)


# =============================================================================
# DSM-5 DIAGNOSTIC CRITERIA
# =============================================================================

DSM5_DISORDERS = {
    "MDD": {
        "name": "Major Depressive Disorder",
        "category": "depressive",
        "required_criteria": ["MDD_A1", "MDD_A2"],  # At least one
        "supporting_criteria": ["MDD_A3", "MDD_A4", "MDD_A5", "MDD_A6", "MDD_A7", "MDD_A8", "MDD_A9"],
        "min_criteria": 5,  # Total including required
        "duration": "2 weeks"
    },
    "GAD": {
        "name": "Generalized Anxiety Disorder",
        "category": "anxiety",
        "required_criteria": ["GAD_A", "GAD_B"],
        "supporting_criteria": ["GAD_C1", "GAD_C2", "GAD_C3", "GAD_C4", "GAD_C5", "GAD_C6"],
        "min_criteria": 3,
        "duration": "6 months"
    },
    "PTSD": {
        "name": "Post-Traumatic Stress Disorder",
        "category": "trauma",
        "required_criteria": ["PTSD_A"],
        "supporting_criteria": ["PTSD_B1", "PTSD_B2", "PTSD_B3", "PTSD_B4", "PTSD_C", "PTSD_D", "PTSD_E"],
        "min_criteria": 4,
        "duration": "1 month"
    },
    "PAN": {
        "name": "Panic Disorder",
        "category": "anxiety",
        "required_criteria": ["PAN_A"],
        "supporting_criteria": ["PAN_B1", "PAN_B2"],
        "min_criteria": 2,
        "duration": "1 month"
    }
}


# =============================================================================
# MCP TOOLS
# =============================================================================

@register_tool(
    name="screen_disorder_categories",
    description="Screen symptoms to identify relevant disorder categories",
    input_schema={
        "type": "object",
        "properties": {"symptoms": {"type": "array"}},
        "required": ["symptoms"]
    },
    agent="diagnosis"
)
def screen_disorder_categories(symptoms: List[Dict]) -> List[str]:
    """Identify which disorder categories to evaluate"""
    categories = {}
    
    for sym in symptoms:
        cat = sym.get("category", "other")
        severity = sym.get("severity", 0.5)
        
        if cat not in categories:
            categories[cat] = {"count": 0, "total_severity": 0}
        
        categories[cat]["count"] += 1
        categories[cat]["total_severity"] += severity
    
    # Rank by weighted score
    ranked = sorted(
        categories.items(),
        key=lambda x: x[1]["count"] * x[1]["total_severity"],
        reverse=True
    )
    
    # Return top 2 categories
    return [cat for cat, _ in ranked[:2]] if ranked else ["depressive"]


@register_tool(
    name="evaluate_disorder_criteria",
    description="Evaluate symptoms against disorder criteria",
    input_schema={
        "type": "object",
        "properties": {
            "disorder_id": {"type": "string"},
            "symptoms": {"type": "array"}
        },
        "required": ["disorder_id", "symptoms"]
    },
    agent="diagnosis"
)
def evaluate_disorder_criteria(disorder_id: str, symptoms: List[Dict]) -> Dict:
    """
    Evaluate symptoms against DSM-5 criteria with weighted scoring.
    Core criteria = 3 points
    Supporting criteria = 1 point
    """
    disorder = DSM5_DISORDERS.get(disorder_id)
    if not disorder:
        return {"error": f"Unknown disorder: {disorder_id}"}
    
    # Collate present criteria
    met_criteria_ids = set()
    for sym in symptoms:
        if sym.get("dsm_criteria_id"):
            met_criteria_ids.add(sym.get("dsm_criteria_id"))
        for crit in sym.get("dsm_criteria", []):
            met_criteria_ids.add(crit)
            
    # Calculate Scores
    required_ids = set(disorder["required_criteria"])
    supporting_ids = set(disorder["supporting_criteria"])
    
    required_met = required_ids.intersection(met_criteria_ids)
    supporting_met = supporting_ids.intersection(met_criteria_ids)
    
    # Weighted Scoring
    # Core criteria are weighted 3x to emphasize their necessity
    score = (len(required_met) * 3) + (len(supporting_met) * 1)
    
    # Max score should be based on a "typical severe case" (e.g. all required + most supporting)
    # But for a basic diagnosis, we shouldn't penalize for not having EVERY symptom.
    # Let's define "Target Score" as the score of a minimally qualifying case + a buffer
    # Min MDD = 1 Core (3pts) + 4 Supp (4pts) = 7 pts. 
    # Max possible = 2 Core (6pts) + 7 Supp (7pts) = 13 pts.
    
    max_possible_score = (len(required_ids) * 3) + (len(supporting_ids) * 1)
    
    # Base confidence is the ratio of score to max_possible_score
    raw_confidence = score / max_possible_score if max_possible_score > 0 else 0
    
    # Adjustments
    has_required = len(required_met) > 0
    min_criteria_needed = disorder["min_criteria"]
    total_count_met = len(required_met) + len(supporting_met)
    met_threshold = total_count_met >= min_criteria_needed and has_required

    # If they meet the diagnostic threshold, confidence should be high (>0.75) regardless of raw score
    if met_threshold:
        # Boost confidence to range [0.8, 1.0] based on severity/extra symptoms
        boost = 0.8 + (0.2 * (score / max_possible_score))
        confidence = min(0.99, boost)
    elif not required_met:
        # Severe penalty if no core symptoms
        confidence = raw_confidence * 0.2
    else:
        # Sub-threshold: Range [0.3, 0.7]
        confidence = raw_confidence * 1.2
        confidence = min(0.7, confidence)

    # Severity Calculation
    
    # Severity Calculation
    avg_symptom_severity = sum(s.get("severity", 0.5) for s in symptoms) / max(1, len(symptoms))
    if avg_symptom_severity > 0.8:
        severity = "severe"
    elif avg_symptom_severity > 0.5:
        severity = "moderate"
    else:
        severity = "mild"

    return {
        "disorder_id": disorder_id,
        "disorder_name": disorder["name"],
        "category": disorder["category"],
        "confidence": round(confidence, 2),
        "severity": severity,
        "diagnosis_met": met_threshold, # Legacy bool for threshold check
        "criteria_met_count": total_count_met,
        "met_criteria_ids": list(met_criteria_ids),
        "score_details": {
            "score": score,
            "max_score": max_possible_score,
            "required_met": len(required_met),
            "supporting_met": len(supporting_met)
        }
    }


@register_tool(
    name="generate_clinical_report",
    description="Generate clinical summary report",
    input_schema={
        "type": "object",
        "properties": {
            "diagnoses": {"type": "array"},
            "symptoms": {"type": "array"}
        },
        "required": ["diagnoses", "symptoms"]
    },
    agent="diagnosis"
)
async def generate_clinical_report(diagnoses: List[Dict], symptoms: List[Dict]) -> str:
    """Generate clinical summary using LLM"""
    try:
        llm = AgentLLMClient(agent_name="Diagnosis")
        
        diag_text = "\n".join([
            f"- {d.get('disorder_name', 'Unknown')}: {d.get('confidence', 0)*100:.0f}% confidence, {d.get('severity', 'moderate')} severity"
            for d in diagnoses if d.get("diagnosis_met")
        ])
        
        sym_text = ", ".join([s.get("name", "") for s in symptoms[:10]])
        
        prompt = f"""Generate a grounded clinical summary based STRICTLY on the evidence provided.

EVIDENCE:
Symptoms: {sym_text}
Diagnoses: {diag_text if diag_text else "No definitive diagnoses met threshold."}

INSTRUCTIONS:
1. Start with "Clinical Impression:".
2. Summarize the patient's presentation using ONLY the cited symptoms.
3. Discuss the primary diagnosis (if any) and why it fits (or doesn't fit).
4. Mention any differential diagnoses that were considered.
5. Conclude with "Recommendations:" for next steps (e.g., specialist referral).
6. CRITICAL: Do NOT mention any symptoms, behaviors, or history not listed in the EVIDENCE section. If evidence is sparse, state that.

FORMAT:
Professional, clinical tone. 2-3 paragraphs.
"""
        
        return await llm.generate_async(prompt, max_tokens=600)
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return "Clinical summary generation pending specialist review."


# =============================================================================
# AGENT
# =============================================================================

class DiagnosisAgentV2(BaseAgent):
    """
    Optimized Diagnosis Agent V2
    
    Features:
    - Decision tree algorithm (2-3 LLM calls)
    - DSM-5 criteria evaluation
    - Multi-disorder assessment
    - Clinical report generation
    """
    
    def __init__(self, llm_client=None, **kwargs):
        super().__init__(agent_name="DiagnosisAgentV2", **kwargs)
        self.llm_client = llm_client or AgentLLMClient(agent_name="Diagnosis")
        self.state_manager = get_state_manager()
    
    async def process(self, state: Dict) -> AgentOutput:
        """Run diagnosis on accumulated symptoms"""
        
        session_id = state.get("session_id")
        patient_id = state.get("patient_id", "")
        
        # Get symptoms from state or params
        conv_state = self.state_manager.get(session_id)
        if conv_state:
            symptoms = [
                {
                    "name": s.name,
                    "severity": s.severity,
                    "category": s.category,
                    "dsm_criteria_id": s.dsm_criteria_id,
                    "dsm_criteria": [s.dsm_criteria_id] if s.dsm_criteria_id else []
                }
                for s in conv_state.symptoms
            ]
        else:
            symptoms = state.get("symptoms", [])
        
        if len(symptoms) < 3:
            return AgentOutput(
                content={"error": "Insufficient symptoms for diagnosis"},
                metadata={"symptom_count": len(symptoms)}
            )
        
        try:
            # STEP 1: Screen categories
            categories = screen_disorder_categories(symptoms)
            self.log_info(f"Screening categories: {categories}")
            
            # STEP 2: Get candidate disorders for each category
            candidates = []
            for cat in categories:
                for disorder_id, disorder in DSM5_DISORDERS.items():
                    if disorder["category"] == cat:
                        candidates.append(disorder_id)
            
            # STEP 3: Evaluate each candidate
            evaluations = []
            for disorder_id in candidates[:4]:  # Limit to top 4
                result = evaluate_disorder_criteria(disorder_id, symptoms)
                if result.get("diagnosis_met") or result.get("confidence", 0) > 0.3:
                    evaluations.append(result)
            
            # Sort by confidence
            evaluations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            # STEP 4: Generate report
            report = await generate_clinical_report(evaluations, symptoms)
            
            # Prepare output
            primary = evaluations[0] if evaluations else None
            differentials = evaluations[1:3] if len(evaluations) > 1 else []
            
            # Update state
            if conv_state and primary:
                conv_state.diagnosis_ready = True
                conv_state.primary_diagnosis = primary
                conv_state.differential_diagnoses = differentials
                self.state_manager.save(conv_state)
            
            # Save to DB
            if primary:
                await self._save_diagnosis_to_db(session_id, patient_id, primary, report)
            
            return AgentOutput(
                content={
                    "primary_diagnosis": primary,
                    "differential_diagnoses": differentials,
                    "clinical_report": report,
                    "symptom_count": len(symptoms),
                    "disorders_evaluated": len(evaluations)
                },
                metadata={
                    "categories_screened": categories,
                    "candidates_evaluated": candidates
                }
            )
            
        except Exception as e:
            self.log_error(f"Diagnosis failed: {e}", exc_info=True)
            return AgentOutput(content={"error": str(e)}, error=str(e))
    
    async def _save_diagnosis_to_db(
        self, 
        session_id: str, 
        patient_id: str, 
        diagnosis: Dict, 
        report: str
    ):
        """Save diagnosis to database"""
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            db = SessionLocal()
            try:
                category_map = {
                    "depressive": "depressive",
                    "anxiety": "anxiety",
                    "trauma": "trauma",
                    "substance": "substance"
                }
                
                db_data = {
                    "disorder_code": diagnosis.get("disorder_id", ""),
                    "disorder_name": diagnosis.get("disorder_name", ""),
                    "category": category_map.get(diagnosis.get("category", ""), "other"),
                    "confidence": diagnosis.get("confidence", 0),
                    "severity": diagnosis.get("severity", "moderate"),
                    "criteria_met": diagnosis.get("met_criteria_ids", []),
                    "criteria_total": diagnosis.get("criteria_required", 0),
                    "is_primary": True,
                    "clinical_report": report
                }
                
                assessment_repo.add_diagnosis(db, session_id, patient_id, db_data)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not save diagnosis to DB: {e}")


__all__ = ["DiagnosisAgentV2"]
