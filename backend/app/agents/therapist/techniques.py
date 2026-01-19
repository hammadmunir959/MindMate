"""
Therapeutic Techniques
======================
Active listening, validation, and other therapeutic communication techniques.
"""

from typing import List, Optional
from enum import Enum


class ConversationPhase(Enum):
    """Phases of therapeutic conversation"""
    RAPPORT = "rapport"           # Building trust (first 3-5 exchanges)
    EXPLORATION = "exploration"   # Main conversation, following patient's lead
    DEEPENING = "deepening"       # Exploring symptoms in depth
    CLOSING = "closing"           # Summarizing and transitioning to results


class EmotionalTone(Enum):
    """Detected emotional tone of the conversation"""
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    SAD = "sad"
    ANGRY = "angry"
    HOPEFUL = "hopeful"
    RESISTANT = "resistant"
    DISTRESSED = "distressed"


class RiskLevel(Enum):
    """Risk assessment level"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class TherapeuticTechniques:
    """
    Collection of therapeutic communication techniques
    for generating empathetic, natural responses.
    """
    
    @staticmethod
    def active_listening(statement: str) -> str:
        """
        Generate an active listening response.
        Reflects back what the patient said to show understanding.
        """
        prefixes = [
            "What I'm hearing is that",
            "It sounds like",
            "So you're saying that",
            "If I understand correctly,",
        ]
        return f"{prefixes[hash(statement) % len(prefixes)]} {statement.lower()}"
    
    @staticmethod
    def validation_responses() -> List[str]:
        """Get validation response templates"""
        return [
            "It makes complete sense that you'd feel that way.",
            "That sounds really difficult to deal with.",
            "Your feelings are completely valid.",
            "Many people struggle with similar experiences.",
            "It's understandable to feel overwhelmed by this.",
            "Thank you for trusting me with this.",
        ]
    
    @staticmethod
    def open_questions() -> List[str]:
        """Get open-ended question templates"""
        return [
            "Can you tell me more about that?",
            "How does that make you feel?",
            "What goes through your mind when that happens?",
            "How has this been affecting your daily life?",
            "When did you first start noticing this?",
            "What do you think might be contributing to this?",
        ]
    
    @staticmethod
    def deepening_questions(topic: str) -> List[str]:
        """Get questions to explore a topic deeper"""
        return [
            f"How often do you experience {topic}?",
            f"When you feel {topic}, how intense would you say it is?",
            f"What usually triggers these feelings of {topic}?",
            f"How long does {topic} typically last?",
            f"Are there times when {topic} is better or worse?",
        ]
    
    @staticmethod
    def transition_phrases() -> List[str]:
        """Get phrases for transitioning between topics"""
        return [
            "Thank you for sharing that. I'd like to understand more about...",
            "That's really helpful to know. Can we also talk about...",
            "I appreciate you opening up about this. Another area I'm curious about is...",
            "What you're describing is important. I'm also wondering about...",
        ]
    
    @staticmethod
    def normalize_statements() -> List[str]:
        """Get statements that normalize the patient's experience"""
        return [
            "It's completely normal to feel this way.",
            "Many people experience something similar.",
            "You're not alone in feeling this.",
            "This is more common than you might think.",
        ]
    
    @staticmethod
    def safety_responses() -> List[str]:
        """Get responses for when safety concerns are detected"""
        return [
            "I want you to know that your safety is really important to me.",
            "What you're sharing sounds really difficult. Are you safe right now?",
            "I'm concerned about what you're telling me. Can we talk more about this?",
            "Thank you for trusting me with this. I want to make sure you're okay.",
        ]
    
    @staticmethod
    def determine_phase(
        message_count: int,
        symptom_count: int,
        has_deep_exploration: bool
    ) -> ConversationPhase:
        """
        Determine the current conversation phase based on session progress.
        """
        if message_count <= 4:
            return ConversationPhase.RAPPORT
        elif symptom_count >= 5 or has_deep_exploration:
            return ConversationPhase.DEEPENING
        else:
            return ConversationPhase.EXPLORATION
    
    @staticmethod
    def detect_risk_keywords(text: str) -> RiskLevel:
        """
        Detect risk level based on keywords in text.
        This is a simple heuristic - real implementation should be more sophisticated.
        """
        text_lower = text.lower()
        
        critical_keywords = [
            "kill myself", "end my life", "suicide", "want to die",
            "no reason to live", "better off dead"
        ]
        
        high_keywords = [
            "hurt myself", "self-harm", "cutting", "don't want to be here",
            "give up", "can't go on"
        ]
        
        moderate_keywords = [
            "hopeless", "worthless", "burden", "no point",
            "exhausted", "can't cope"
        ]
        
        for keyword in critical_keywords:
            if keyword in text_lower:
                return RiskLevel.CRITICAL
        
        for keyword in high_keywords:
            if keyword in text_lower:
                return RiskLevel.HIGH
        
        for keyword in moderate_keywords:
            if keyword in text_lower:
                return RiskLevel.MODERATE
        
        return RiskLevel.NONE


__all__ = [
    "ConversationPhase",
    "EmotionalTone", 
    "RiskLevel",
    "TherapeuticTechniques"
]
