"""
MCP Tool: Evaluate Criteria
===========================
Evaluates symptoms against DSM-5 criteria for a specific disorder.
"""

from typing import Dict, List, Any, Optional
import json
import re


TOOL_SCHEMA = {
    "name": "evaluate_criteria",
    "description": "Evaluate symptoms against DSM-5 criteria for a specific disorder",
    "inputSchema": {
        "type": "object",
        "properties": {
            "disorder_id": {
                "type": "string",
                "description": "DSM-5 disorder ID (e.g., MDD, GAD)"
            },
            "symptoms": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["disorder_id", "symptoms"]
    }
}


async def execute(
    disorder_id: str,
    symptoms: List[Dict],
    criteria_db: Dict = None,
    llm_client = None
) -> Dict[str, Any]:
    """
    Evaluate if patient symptoms meet DSM-5 criteria for a disorder.
    
    Returns:
        - criteria_met: bool
        - met_count: int
        - required_count: int
        - confidence: float
        - met_criteria_ids: list
    """
    # Load criteria if not provided
    if criteria_db is None:
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, "resources", "dsm_criteria.json")
        
        with open(json_path, "r") as f:
            data = json.load(f)
            criteria_db = data.get("disorders", {})
    
    disorder_def = criteria_db.get(disorder_id)
    if not disorder_def:
        return {
            "criteria_met": False,
            "error": f"Disorder {disorder_id} not found"
        }
    
    # Format symptoms for LLM
    symptom_text = "\n".join([
        f"- {s.get('name', 'unknown')} (severity: {s.get('severity', 0.5):.1f})"
        for s in symptoms
    ])
    
    criteria_list = disorder_def.get("criteria", [])
    criteria_text = "\n".join([
        f"{c['criterion_id']}: {c['text']}"
        for c in criteria_list
    ])
    
    # Handle None value for minimum_criteria_count
    min_count = disorder_def.get("minimum_criteria_count")
    if min_count is None:
        min_count = max(1, len(criteria_list) // 2)  # Default to half of criteria
    
    prompt = f"""Evaluate if the patient meets criteria for {disorder_def['disorder_name']}.

Patient Symptoms:
{symptom_text}

DSM-5 Criteria for {disorder_def['disorder_name']}:
{criteria_text}

Minimum Required: {min_count} criteria

Instructions:
1. Match symptoms to criteria using clinical judgment
2. Consider severity (low severity may not fully meet criteria)
3. Be conservative - require clear evidence

Return ONLY JSON:
{{"met_criteria_ids": ["CRITERION_ID1", "CRITERION_ID2"], "reasoning": "brief"}}
"""
    
    met_ids = []
    reasoning = ""
    
    if llm_client:
        try:
            response = await llm_client.generate_async(
                prompt=prompt,
                system_prompt="You are a clinical diagnostic assistant. Output valid JSON only.",
                temperature=0.1,
                max_tokens=300
            )
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                met_ids = result.get("met_criteria_ids", [])
                reasoning = result.get("reasoning", "")
        except Exception as e:
            # Fallback to simple matching
            pass
    
    if not met_ids:
        # Fallback: Simple keyword matching
        symptom_names = " ".join([s.get("name", "").lower() for s in symptoms])
        for criterion in criteria_list:
            criterion_text = criterion.get("text", "").lower()
            keywords = criterion_text.split()[:5]  # First 5 words as keywords
            if any(kw in symptom_names for kw in keywords if len(kw) > 4):
                met_ids.append(criterion["criterion_id"])
    
    # Evaluate
    criteria_met = len(met_ids) >= min_count
    confidence = len(met_ids) / len(criteria_list) if criteria_list else 0
    
    # Determine severity
    ratio = len(met_ids) / len(criteria_list) if criteria_list else 0
    if ratio >= 0.8:
        severity = "severe"
    elif ratio >= 0.6:
        severity = "moderate"
    else:
        severity = "mild"
    
    return {
        "disorder_id": disorder_id,
        "disorder_name": disorder_def["disorder_name"],
        "category": disorder_def.get("category", "unknown"),
        "criteria_met": criteria_met,
        "met_count": len(met_ids),
        "required_count": min_count,
        "total_criteria": len(criteria_list),
        "confidence": round(confidence, 2),
        "severity": severity,
        "met_criteria_ids": met_ids,
        "reasoning": reasoning
    }
