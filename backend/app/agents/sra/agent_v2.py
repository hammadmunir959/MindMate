"""
Optimized SRA V2
================
Async symptom extraction with DSM-5 mapping.
Uses MCP tools for structured extraction.
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
import re

from app.agents.base import BaseAgent, AgentOutput
from app.agents.core import (
    Symptom, ProcessedResponse, ConversationState, 
    get_state_manager, get_registry, register_tool
)
from app.core.llm_client import AgentLLMClient

logger = logging.getLogger(__name__)


# =============================================================================
# SYMPTOM DATABASE
# =============================================================================

DSM5_SYMPTOM_MAP = {
    # Depressive symptoms
    "sad": {"category": "depressive", "criteria": ["MDD_A1"]},
    "depressed": {"category": "depressive", "criteria": ["MDD_A1"]},
    "hopeless": {"category": "depressive", "criteria": ["MDD_A1"]},
    "down": {"category": "depressive", "criteria": ["MDD_A1"]},
    "lost interest": {"category": "depressive", "criteria": ["MDD_A2"]},
    "no motivation": {"category": "depressive", "criteria": ["MDD_A2"]},
    "anhedonia": {"category": "depressive", "criteria": ["MDD_A2"]},
    "sleep": {"category": "depressive", "criteria": ["MDD_A4"]},
    "insomnia": {"category": "depressive", "criteria": ["MDD_A4"]},
    "fatigue": {"category": "depressive", "criteria": ["MDD_A6"]},
    "tired": {"category": "depressive", "criteria": ["MDD_A6"]},
    "worthless": {"category": "depressive", "criteria": ["MDD_A7"]},
    "guilt": {"category": "depressive", "criteria": ["MDD_A7"]},
    "concentration": {"category": "depressive", "criteria": ["MDD_A8"]},
    "appetite": {"category": "depressive", "criteria": ["MDD_A3"]},
    
    # Anxiety symptoms
    "anxious": {"category": "anxiety", "criteria": ["GAD_A"]},
    "worried": {"category": "anxiety", "criteria": ["GAD_A"]},
    "nervous": {"category": "anxiety", "criteria": ["GAD_A"]},
    "panic": {"category": "anxiety", "criteria": ["PAN_A"]},
    "fear": {"category": "anxiety", "criteria": ["GAD_A"]},
    "on edge": {"category": "anxiety", "criteria": ["GAD_C1"]},
    "restless": {"category": "anxiety", "criteria": ["GAD_C1"]},
    
    # Trauma symptoms
    "flashback": {"category": "trauma", "criteria": ["PTSD_B1"]},
    "nightmare": {"category": "trauma", "criteria": ["PTSD_B2"]},
    "trauma": {"category": "trauma", "criteria": ["PTSD_A"]},
    "triggered": {"category": "trauma", "criteria": ["PTSD_B4"]},
    
    # Substance
    "alcohol": {"category": "substance", "criteria": ["SUD_A"]},
    "drinking": {"category": "substance", "criteria": ["AUD_A"]},
    "drug": {"category": "substance", "criteria": ["SUD_A"]},
}

SEVERITY_WORDS = {
    0.8: ["extremely", "unbearable", "constant", "severe", "all the time"],
    0.6: ["very", "really", "often", "frequently", "most days"],
    0.4: ["sometimes", "occasionally", "moderate", "a bit"],
    0.2: ["rarely", "slightly", "a little", "mild"]
}


# =============================================================================
# MCP TOOLS
# =============================================================================

@register_tool(
    name="extract_symptoms_fast",
    description="Fast keyword-based symptom extraction",
    input_schema={
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"]
    },
    agent="sra"
)
def extract_symptoms_fast(message: str) -> List[Dict]:
    """Fast NER-style extraction using keyword matching"""
    message_lower = message.lower()
    found = []
    
    for keyword, mapping in DSM5_SYMPTOM_MAP.items():
        if keyword in message_lower:
            # Estimate severity
            severity = 0.5
            for sev_score, sev_words in SEVERITY_WORDS.items():
                if any(sw in message_lower for sw in sev_words):
                    severity = sev_score
                    break
            
            found.append({
                "name": keyword,
                "category": mapping["category"],
                "dsm_criteria": mapping["criteria"],
                "severity": severity,
                "confidence": 0.7
            })
    
    return found


@register_tool(
    name="extract_symptoms_llm",
    description="LLM-based semantic symptom extraction",
    input_schema={
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "context": {"type": "string"}
        },
        "required": ["message"]
    },
    agent="sra"
)
async def extract_symptoms_llm(message: str, context: str = "") -> List[Dict]:
    """LLM-based deep extraction using robust JSON schema"""
    try:
        from app.core.llm_client import AgentLLMClient
        llm = AgentLLMClient(agent_name="SRA")
        
        prompt = f"""Analyze the patient's message for mental health symptoms.

Patient Message: "{message}"
Conversation Context: "{context}"

INSTRUCTIONS:
1. Identify all mental health symptoms mentioned or implied.
2. For each, assign a severity score (0.0 - 1.0) based on modifiers (e.g., "a little" = 0.2, "unbearable" = 0.9).
3. Map to one of these categories: depressive, anxiety, trauma, substance, eating, psychotic, other.
4. Return ONLY a valid JSON array of objects.

JSON SCHEMA:
[
  {{
    "name": "string (canonical clinical name, e.g. 'insomnia' instead of 'check waking up')",
    "severity": float (0.0-1.0),
    "category": "string",
    "dsm_criteria": ["string"] (optional IDs if known, e.g. "MDD_A1"),
    "duration": "string" (optional),
    "frequency": "string" (optional)
  }}
]

Response (JSON Array ONLY):"""
        
        response = await llm.generate_async(prompt, temperature=0.0, max_tokens=500)
        
        # Robust JSON Parsing
        import json
        
        clean_response = response.strip()
        # Remove markdown code blocks if present
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        
        # Ensure it starts with [
        if not clean_response.startswith("["):
             match = re.search(r'\[.*\]', clean_response, re.DOTALL)
             if match:
                 clean_response = match.group()
             else:
                 return []

        data = json.loads(clean_response)
        if isinstance(data, list):
            return data
        return []
        
    except Exception as e:
        logger.warning(f"LLM extraction failed: {e}")
        return []

# Fuzzy matching helper
def calculate_similarity(s1: str, s2: str) -> float:
    """Simple character-based similarity (Jaccard-like or substring)"""
    s1, s2 = s1.lower(), s2.lower()
    if s1 == s2: return 1.0
    if s1 in s2 or s2 in s1: return 0.8
    
    # Simple set overlap for multi-word symptoms
    set1 = set(s1.split())
    set2 = set(s2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


class SRAAgentV2(BaseAgent):
    """
    Optimized Symptom Recognition Agent V2.1
    
    Features:
    - Hybrid extraction (fast NER + LLM)
    - Robust JSON Parsing
    - Smart Fuzzy Merging
    - State integration
    """
    
    def __init__(self, llm_client=None, **kwargs):
        super().__init__(agent_name="SRAAgentV2", **kwargs)
        self.llm_client = llm_client or AgentLLMClient(agent_name="SRA")
        self.state_manager = get_state_manager()
    
    async def process(self, state: Dict) -> AgentOutput:
        """Process message and extract symptoms"""
        
        session_id = state.get("session_id")
        user_message = state.get("user_message", "")
        
        if not session_id or len(user_message.strip()) < 5:
            return AgentOutput(content=[], metadata={"skipped": True})
        
        conv_state = self.state_manager.get(session_id)
        context = ""
        if conv_state and conv_state.messages:
            # Get last 3 messages for context
            context = " ".join([m.get("content", "") for m in conv_state.messages[-3:]])
        
        try:
            # Run both extraction methods in parallel
            fast_task = asyncio.get_event_loop().run_in_executor(
                None, extract_symptoms_fast, user_message
            )
            llm_task = extract_symptoms_llm(user_message, context)
            
            fast_results, llm_results = await asyncio.gather(fast_task, llm_task)
            
            # Merge results (Smart Fuzzy Merge)
            merged = self._merge_symptoms(fast_results, llm_results)
            
            # Convert to Symptom objects
            new_symptoms = []
            for sym_data in merged:
                symptom = Symptom(
                    name=sym_data.get("name", "unknown"),
                    severity=sym_data.get("severity", 0.5),
                    confidence=sym_data.get("confidence", 0.7),
                    category=sym_data.get("category", "other"),
                    dsm_criteria_id=sym_data.get("dsm_criteria", [None])[0] if sym_data.get("dsm_criteria") else None,
                    source_message=user_message[:100]
                )
                new_symptoms.append(symptom)
                
                # Update state if exists
                if conv_state:
                    conv_state.add_symptom(symptom)
            
            if conv_state:
                self.state_manager.save(conv_state)
            
            # Also save to DB
            await self._save_symptoms_to_db(session_id, new_symptoms)
            
            if new_symptoms:
                self.log_info(f"SRA: Extracted {len(new_symptoms)} symptoms for {session_id}")
            
            return AgentOutput(
                content=[{"name": s.name, "severity": s.severity} for s in new_symptoms],
                metadata={
                    "count": len(new_symptoms),
                    "fast_count": len(fast_results),
                    "llm_count": len(llm_results)
                }
            )
            
        except Exception as e:
            self.log_error(f"SRA extraction failed: {e}", exc_info=True)
            return AgentOutput(content=[], error=str(e))
    
    def _merge_symptoms(self, fast: List[Dict], llm: List[Dict]) -> List[Dict]:
        """Merge symptom lists using fuzzy matching"""
        merged_map = {}
        
        # 1. Process LLM results (High Priority)
        for sym in llm:
            name = sym.get("name", "").lower()
            if not name: continue
            sym["confidence"] = 0.9  # High confidence for LLM
            sym["source"] = "llm"
            merged_map[name] = sym
            
        # 2. Process Fast results (Merge if similar)
        for sym in fast:
            fast_name = sym.get("name", "").lower()
            if not fast_name: continue
            
            matched = False
            # Check against existing merged items
            for existing_name, existing_sym in merged_map.items():
                similarity = calculate_similarity(fast_name, existing_name)
                
                if similarity > 0.7:  # Threshold for "same symptom"
                    # Merge logic:
                    # - Keep LLM name (usually more canonical)
                    # - Keep higher severity
                    # - Keep LLM category if available
                    existing_sym["severity"] = max(existing_sym["severity"], sym["severity"])
                    # If fast match had specific DSM criteria and LLM didn't, take it
                    if not existing_sym.get("dsm_criteria") and sym.get("dsm_criteria"):
                        existing_sym["dsm_criteria"] = sym["dsm_criteria"]
                    
                    matched = True
                    break
            
            if not matched:
                sym["confidence"] = 0.6  # Lower confidence for keyword match
                sym["source"] = "fast"
                merged_map[fast_name] = sym
                
        return list(merged_map.values())
    
    async def _save_symptoms_to_db(self, session_id: str, symptoms: List[Symptom]):
        """Save symptoms to database"""
        try:
            from app.db.session import SessionLocal
            from app.db.repositories_new import assessment_repo
            
            db = SessionLocal()
            try:
                category_map = {
                    "depressive": "depressive",
                    "anxiety": "anxiety",
                    "trauma": "trauma",
                    "substance": "substance",
                    "other": "other"
                }
                
                for symptom in symptoms:
                    db_data = {
                        "symptom_name": symptom.name,
                        "severity": symptom.severity,
                        "category": category_map.get(symptom.category, "other"),
                        "confidence": symptom.confidence
                    }
                    assessment_repo.upsert_symptom(db, session_id, db_data)
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"Could not save symptoms to DB: {e}")


__all__ = ["SRAAgentV2"]
