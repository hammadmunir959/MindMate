"""
MCP Tool: Get Candidate Disorders
=================================
Filters disorders within categories by core symptom match.
"""

from typing import Dict, List, Any


TOOL_SCHEMA = {
    "name": "get_candidate_disorders",
    "description": "Get disorders within categories, filtered by core symptom match",
    "inputSchema": {
        "type": "object",
        "properties": {
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "DSM-5 category names"
            },
            "symptoms": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["categories", "symptoms"]
    }
}


async def execute(
    categories: List[str],
    symptoms: List[Dict]
) -> Dict[str, Any]:
    """
    Get candidate disorders by:
    1. Listing all disorders in the categories
    2. Filtering by core symptom presence
    """
    from app.agents.diagnosis.decision_tree import (
        get_candidate_disorders,
        CATEGORY_DISORDERS,
        CORE_SYMPTOMS
    )
    
    # Get candidates using decision tree logic
    candidates = get_candidate_disorders(categories, symptoms)
    
    # Build metadata for each candidate
    disorder_info = []
    for disorder_id in candidates:
        category = None
        for cat, disorders in CATEGORY_DISORDERS.items():
            if disorder_id in disorders:
                category = cat
                break
        
        core_required = CORE_SYMPTOMS.get(disorder_id, {}).get("any_of", [])
        
        disorder_info.append({
            "disorder_id": disorder_id,
            "category": category,
            "core_symptoms_checked": core_required[:3]  # Show first 3
        })
    
    return {
        "candidates": candidates,
        "details": disorder_info,
        "total_in_categories": sum(
            len(CATEGORY_DISORDERS.get(c, [])) for c in categories
        ),
        "filtered_count": len(candidates)
    }
