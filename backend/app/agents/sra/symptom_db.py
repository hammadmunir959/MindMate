"""
DSM-5 Symptom Database
======================
Reference database of DSM-5 symptoms and criteria mappings.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DisorderCategory(Enum):
    """DSM-5 disorder categories"""
    DEPRESSIVE = "depressive_disorders"
    ANXIETY = "anxiety_disorders"
    TRAUMA = "trauma_related"
    BIPOLAR = "bipolar_disorders"
    OCD = "obsessive_compulsive"
    EATING = "eating_disorders"
    SLEEP = "sleep_disorders"
    SUBSTANCE = "substance_related"
    PERSONALITY = "personality_disorders"


@dataclass
class Symptom:
    """Represents an extracted symptom"""
    name: str
    category: DisorderCategory
    severity: float = 0.5  # 0-1 scale
    frequency: Optional[str] = None  # daily, weekly, etc.
    duration: Optional[str] = None  # weeks, months, years
    dsm5_criteria: List[str] = field(default_factory=list)
    source_text: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "severity": self.severity,
            "frequency": self.frequency,
            "duration": self.duration,
            "dsm5_criteria": self.dsm5_criteria,
            "source_text": self.source_text,
        }


class DSM5SymptomDatabase:
    """
    Reference database of DSM-5 symptoms and their mappings.
    
    This provides:
    - Symptom keyword matching
    - DSM-5 criteria mapping
    - Severity inference patterns
    """
    
    # Common symptom patterns and their categories
    SYMPTOM_PATTERNS: Dict[str, Dict] = {
        # Depressive symptoms
        "sad": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A1"]},
        "depressed": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A1"]},
        "hopeless": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A1", "A2"]},
        "worthless": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A7"]},
        "guilty": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A7"]},
        "no energy": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A6"]},
        "fatigue": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A6"]},
        "tired": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A6"]},
        "can't sleep": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A4"]},
        "insomnia": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A4"]},
        "sleeping too much": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A4"]},
        "no appetite": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A3"]},
        "eating too much": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A3"]},
        "can't concentrate": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A8"]},
        "death": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A9"]},
        "suicide": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A9"]},
        "no interest": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A2"]},
        "anhedonia": {"category": DisorderCategory.DEPRESSIVE, "criteria": ["A2"]},
        
        # Anxiety symptoms
        "anxious": {"category": DisorderCategory.ANXIETY, "criteria": ["A1"]},
        "worried": {"category": DisorderCategory.ANXIETY, "criteria": ["A1"]},
        "nervous": {"category": DisorderCategory.ANXIETY, "criteria": ["A1"]},
        "panic": {"category": DisorderCategory.ANXIETY, "criteria": ["A1"]},
        "restless": {"category": DisorderCategory.ANXIETY, "criteria": ["A3"]},
        "on edge": {"category": DisorderCategory.ANXIETY, "criteria": ["A3"]},
        "tense": {"category": DisorderCategory.ANXIETY, "criteria": ["A3"]},
        "racing heart": {"category": DisorderCategory.ANXIETY, "criteria": ["physical"]},
        "sweating": {"category": DisorderCategory.ANXIETY, "criteria": ["physical"]},
        "trembling": {"category": DisorderCategory.ANXIETY, "criteria": ["physical"]},
        "shortness of breath": {"category": DisorderCategory.ANXIETY, "criteria": ["physical"]},
        "dread": {"category": DisorderCategory.ANXIETY, "criteria": ["A1"]},
        "fear": {"category": DisorderCategory.ANXIETY, "criteria": ["A1"]},
        
        # Trauma symptoms
        "flashback": {"category": DisorderCategory.TRAUMA, "criteria": ["B3"]},
        "nightmare": {"category": DisorderCategory.TRAUMA, "criteria": ["B2"]},
        "triggered": {"category": DisorderCategory.TRAUMA, "criteria": ["B4"]},
        "avoidance": {"category": DisorderCategory.TRAUMA, "criteria": ["C"]},
        "numb": {"category": DisorderCategory.TRAUMA, "criteria": ["D"]},
        "hypervigilant": {"category": DisorderCategory.TRAUMA, "criteria": ["E3"]},
        "startle": {"category": DisorderCategory.TRAUMA, "criteria": ["E4"]},
        
        # Bipolar symptoms
        "manic": {"category": DisorderCategory.BIPOLAR, "criteria": ["A"]},
        "high energy": {"category": DisorderCategory.BIPOLAR, "criteria": ["B2"]},
        "racing thoughts": {"category": DisorderCategory.BIPOLAR, "criteria": ["B4"]},
        "grandiose": {"category": DisorderCategory.BIPOLAR, "criteria": ["B1"]},
        "decreased sleep": {"category": DisorderCategory.BIPOLAR, "criteria": ["B2"]},
        "impulsive": {"category": DisorderCategory.BIPOLAR, "criteria": ["B7"]},
        "mood swings": {"category": DisorderCategory.BIPOLAR, "criteria": ["A"]},
    }
    
    # Severity modifiers
    SEVERITY_MODIFIERS: Dict[str, float] = {
        # High severity
        "always": 0.9,
        "constantly": 0.9,
        "every day": 0.85,
        "severe": 0.85,
        "extreme": 0.9,
        "unbearable": 0.95,
        "overwhelming": 0.85,
        
        # Moderate severity
        "often": 0.7,
        "frequently": 0.7,
        "most days": 0.7,
        "moderate": 0.6,
        "regularly": 0.65,
        
        # Low severity
        "sometimes": 0.4,
        "occasionally": 0.35,
        "mild": 0.3,
        "rarely": 0.2,
        "slight": 0.25,
    }
    
    # Duration patterns
    DURATION_PATTERNS: Dict[str, str] = {
        "days": "days",
        "week": "weeks",
        "weeks": "weeks",
        "month": "months",
        "months": "months",
        "year": "years",
        "years": "years",
        "forever": "years",
        "long time": "months",
        "recently": "weeks",
    }
    
    @classmethod
    def match_symptoms(cls, text: str) -> List[Dict]:
        """
        Match symptoms in text against the database.
        
        Args:
            text: User input text
            
        Returns:
            List of matched symptom dictionaries
        """
        text_lower = text.lower()
        matches = []
        
        for pattern, info in cls.SYMPTOM_PATTERNS.items():
            if pattern in text_lower:
                severity = cls._infer_severity(text_lower)
                duration = cls._infer_duration(text_lower)
                
                matches.append({
                    "name": pattern,
                    "category": info["category"].value,
                    "criteria": info["criteria"],
                    "severity": severity,
                    "duration": duration,
                    "source_text": text[:100],
                })
        
        return matches
    
    @classmethod
    def _infer_severity(cls, text: str) -> float:
        """Infer severity from text modifiers"""
        for modifier, severity in cls.SEVERITY_MODIFIERS.items():
            if modifier in text:
                return severity
        return 0.5  # Default moderate
    
    @classmethod
    def _infer_duration(cls, text: str) -> Optional[str]:
        """Infer duration from text"""
        for pattern, duration in cls.DURATION_PATTERNS.items():
            if pattern in text:
                return duration
        return None
    
    @classmethod
    def get_disorder_criteria(cls, category: DisorderCategory) -> Dict:
        """Get DSM-5 criteria for a disorder category"""
        criteria_map = {
            DisorderCategory.DEPRESSIVE: {
                "name": "Major Depressive Disorder",
                "code": "296.xx",
                "required_criteria": ["A1 or A2", "5+ symptoms", "2+ weeks"],
                "criteria": {
                    "A1": "Depressed mood",
                    "A2": "Diminished interest/pleasure",
                    "A3": "Weight/appetite change",
                    "A4": "Sleep disturbance",
                    "A5": "Psychomotor changes",
                    "A6": "Fatigue",
                    "A7": "Worthlessness/guilt",
                    "A8": "Concentration problems",
                    "A9": "Thoughts of death",
                }
            },
            DisorderCategory.ANXIETY: {
                "name": "Generalized Anxiety Disorder",
                "code": "300.02",
                "required_criteria": ["A", "B", "6+ months"],
                "criteria": {
                    "A1": "Excessive anxiety and worry",
                    "A2": "Difficulty controlling worry",
                    "A3": "Restlessness",
                    "A4": "Fatigue",
                    "A5": "Concentration problems",
                    "A6": "Irritability",
                    "A7": "Muscle tension",
                    "A8": "Sleep disturbance",
                }
            },
            # Add more as needed
        }
        return criteria_map.get(category, {})


__all__ = ["DSM5SymptomDatabase", "Symptom", "DisorderCategory"]
