"""
MCP Tool: Screen Categories
===========================
Identifies top 2 DSM-5 disorder categories from symptoms using LLM.
"""

from typing import Dict, List, Any


TOOL_SCHEMA = {
    "name": "screen_categories",
    "description": "Identify top 2 DSM-5 disorder categories from patient symptoms",
    "inputSchema": {
        "type": "object",
        "properties": {
            "symptoms": {
                "type": "array",
                "description": "List of symptom objects with name and severity",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "severity": {"type": "number"}
                    }
                }
            }
        },
        "required": ["symptoms"]
    }
}

CATEGORIES = [
    "mood_disorders",
    "anxiety_disorders", 
    "trauma_stressor_disorders",
    "substance_use_disorders",
    "neurodevelopmental_disorders",
    "obsessive_compulsive_disorders",
    "feeding_eating_disorders",
    "sleep_wake_disorders"
]


async def execute(
    symptoms: List[Dict],
    llm_client=None
) -> Dict[str, Any]:
    """
    Screen symptoms to identify most likely disorder categories.
    
    Uses LLM for nuanced analysis, falls back to keyword matching.
    """
    if not symptoms:
        return {"categories": ["mood_disorders"], "confidence": 0.5}
    
    # Format symptoms for LLM
    symptom_text = "\n".join([
        f"- {s.get('name', 'unknown')} (severity: {s.get('severity', 0.5):.1f})"
        for s in symptoms
    ])
    
    prompt = f"""You are a clinical screening assistant. Given these patient symptoms, identify the TOP 2 most likely DSM-5 disorder categories.

Patient Symptoms:
{symptom_text}

Available Categories:
1. mood_disorders (depression, bipolar)
2. anxiety_disorders (GAD, panic, phobias)
3. trauma_stressor_disorders (PTSD, adjustment)
4. substance_use_disorders
5. neurodevelopmental_disorders (ADHD)
6. obsessive_compulsive_disorders (OCD)
7. feeding_eating_disorders
8. sleep_wake_disorders

Return ONLY a JSON object:
{{"categories": ["category1", "category2"], "reasoning": "brief explanation"}}
"""
    
    if llm_client:
        try:
            response = await llm_client.generate_async(
                prompt=prompt,
                system_prompt="You are a clinical screening assistant. Output valid JSON only.",
                temperature=0.1,
                max_tokens=200
            )
            
            import json
            import re
            
            # Parse JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                categories = result.get("categories", [])
                
                # Validate categories
                valid_cats = [c for c in categories if c in CATEGORIES]
                if valid_cats:
                    return {
                        "categories": valid_cats[:2],
                        "reasoning": result.get("reasoning", ""),
                        "confidence": 0.85
                    }
        except Exception as e:
            pass  # Fall back to keyword matching
    
    # Fallback: Use decision tree module
    from app.agents.diagnosis.decision_tree import screen_categories_from_symptoms
    categories = screen_categories_from_symptoms(symptoms)
    
    return {
        "categories": categories,
        "reasoning": "Keyword-based screening (LLM unavailable)",
        "confidence": 0.7
    }
