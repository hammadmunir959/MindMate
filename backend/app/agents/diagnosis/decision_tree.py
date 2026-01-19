"""
Decision Tree Module
====================
Maps symptoms to disorder categories and provides filtering logic.
"""

from typing import List, Dict, Set

# Category → Disorder mapping
CATEGORY_DISORDERS = {
    "mood_disorders": ["MDD", "BIPOLAR"],
    "anxiety_disorders": ["GAD", "PANIC", "SOCIAL_ANXIETY", "SPECIFIC_PHOBIA", "AGORAPHOBIA"],
    "trauma_stressor_disorders": ["PTSD", "ADJUSTMENT"],
    "substance_use_disorders": ["SUBSTANCE_USE"],
    "neurodevelopmental_disorders": ["ADHD"],
    "obsessive_compulsive_disorders": ["OCD"],
    "feeding_eating_disorders": ["ANOREXIA"],
    "sleep_wake_disorders": ["INSOMNIA"]
}

# Symptom keywords → Category mapping (for fast screening)
SYMPTOM_CATEGORY_MAP = {
    # Mood indicators
    "sad": "mood_disorders",
    "depressed": "mood_disorders",
    "hopeless": "mood_disorders",
    "worthless": "mood_disorders",
    "suicidal": "mood_disorders",
    "elevated mood": "mood_disorders",
    "grandiosity": "mood_disorders",
    "manic": "mood_disorders",
    
    # Anxiety indicators
    "anxious": "anxiety_disorders",
    "worry": "anxiety_disorders",
    "panic": "anxiety_disorders",
    "fear": "anxiety_disorders",
    "nervous": "anxiety_disorders",
    "restless": "anxiety_disorders",
    "avoidance": "anxiety_disorders",
    "phobia": "anxiety_disorders",
    
    # Trauma indicators
    "trauma": "trauma_stressor_disorders",
    "flashback": "trauma_stressor_disorders",
    "nightmare": "trauma_stressor_disorders",
    "stressor": "trauma_stressor_disorders",
    "hypervigilant": "trauma_stressor_disorders",
    
    # Substance indicators
    "substance": "substance_use_disorders",
    "alcohol": "substance_use_disorders",
    "drug": "substance_use_disorders",
    "craving": "substance_use_disorders",
    "withdrawal": "substance_use_disorders",
    "tolerance": "substance_use_disorders",
    
    # ADHD indicators
    "attention": "neurodevelopmental_disorders",
    "hyperactive": "neurodevelopmental_disorders",
    "impulsive": "neurodevelopmental_disorders",
    "distracted": "neurodevelopmental_disorders",
    "fidgeting": "neurodevelopmental_disorders",
    
    # OCD indicators
    "obsession": "obsessive_compulsive_disorders",
    "compulsion": "obsessive_compulsive_disorders",
    "intrusive thoughts": "obsessive_compulsive_disorders",
    "repetitive": "obsessive_compulsive_disorders",
    
    # Eating indicators
    "weight loss": "feeding_eating_disorders",
    "body image": "feeding_eating_disorders",
    "eating": "feeding_eating_disorders",
    "restricting": "feeding_eating_disorders",
    
    # Sleep indicators
    "insomnia": "sleep_wake_disorders",
    "sleep": "sleep_wake_disorders",
    "fatigue": "sleep_wake_disorders",  # Also mood
    "tired": "sleep_wake_disorders",
}

# Core symptoms required for each disorder (for fast rule-out)
CORE_SYMPTOMS = {
    "MDD": {
        "any_of": ["depressed mood", "anhedonia", "loss of interest"],
        "threshold": 1
    },
    "BIPOLAR": {
        "any_of": ["elevated mood", "irritable mood", "increased energy", "grandiosity"],
        "threshold": 2
    },
    "GAD": {
        "any_of": ["excessive worry", "anxiety", "difficulty controlling worry"],
        "threshold": 1
    },
    "PANIC": {
        "any_of": ["panic attack", "palpitations", "fear of dying", "shortness of breath"],
        "threshold": 2
    },
    "SOCIAL_ANXIETY": {
        "any_of": ["social fear", "fear of scrutiny", "embarrassment", "social avoidance"],
        "threshold": 1
    },
    "PTSD": {
        "any_of": ["trauma", "flashback", "nightmare", "hypervigilance", "avoidance"],
        "threshold": 2
    },
    "OCD": {
        "any_of": ["obsession", "compulsion", "intrusive thoughts", "repetitive behavior"],
        "threshold": 1
    },
    "ADHD": {
        "any_of": ["inattention", "hyperactivity", "impulsivity", "difficulty concentrating"],
        "threshold": 2
    },
    "SUBSTANCE_USE": {
        "any_of": ["substance use", "craving", "withdrawal", "tolerance"],
        "threshold": 1
    }
}


def screen_categories_from_symptoms(symptoms: List[Dict]) -> List[str]:
    """
    Fast screening: Map symptoms to most likely categories.
    Returns top 2 categories.
    """
    category_scores: Dict[str, float] = {}
    
    for symptom in symptoms:
        name = symptom.get("name", "").lower()
        severity = symptom.get("severity", 0.5)
        
        # Check each keyword
        for keyword, category in SYMPTOM_CATEGORY_MAP.items():
            if keyword in name:
                category_scores[category] = category_scores.get(category, 0) + severity
    
    # Sort and return top 2
    sorted_categories = sorted(
        category_scores.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    return [cat for cat, _ in sorted_categories[:2]] if sorted_categories else ["mood_disorders"]


def get_candidate_disorders(
    categories: List[str], 
    symptoms: List[Dict]
) -> List[str]:
    """
    Get disorders within categories, filtered by core symptom match.
    """
    candidates = []
    symptom_names = [s.get("name", "").lower() for s in symptoms]
    symptom_text = " ".join(symptom_names)
    
    for category in categories:
        disorders = CATEGORY_DISORDERS.get(category, [])
        
        for disorder_id in disorders:
            if disorder_id in CORE_SYMPTOMS:
                core = CORE_SYMPTOMS[disorder_id]
                matches = sum(
                    1 for keyword in core["any_of"]
                    if keyword.lower() in symptom_text
                )
                if matches >= core["threshold"]:
                    candidates.append(disorder_id)
            else:
                # No core symptom filter, include by default
                candidates.append(disorder_id)
    
    return list(set(candidates))  # Deduplicate


def get_disorders_for_category(category: str) -> List[str]:
    """Get all disorders in a category."""
    return CATEGORY_DISORDERS.get(category, [])


__all__ = [
    "CATEGORY_DISORDERS",
    "SYMPTOM_CATEGORY_MAP", 
    "CORE_SYMPTOMS",
    "screen_categories_from_symptoms",
    "get_candidate_disorders",
    "get_disorders_for_category"
]
