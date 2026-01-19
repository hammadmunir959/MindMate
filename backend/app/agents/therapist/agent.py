"""
Therapist Agent
===============
Main agent for conducting natural, empathetic therapeutic conversations.
"""

from typing import Dict, List, Optional, Any
import asyncio

from app.agents.base import BaseAgent, AgentOutput
from app.agents.therapist.prompts import (
    THERAPIST_SYSTEM_PROMPT,
    GREETING_PROMPT,
    FOLLOW_UP_PROMPT,
)
from app.agents.therapist.techniques import (
    TherapeuticTechniques,
    ConversationPhase,
    RiskLevel,
)
from app.core.llm_client import AgentLLMClient


class TherapistAgent(BaseAgent):
    """
    Therapist Agent for natural, context-aware therapeutic conversations.
    
    Features:
    - Dynamic question generation based on context
    - Active listening and validation techniques
    - Conversation phase management
    - Risk detection and safety responses
    - Integration with SRA symptom data
    - SCID-based interview guidance (NEW)
    """
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="TherapistAgent", **kwargs)
        self.techniques = TherapeuticTechniques()
        self.llm_client = AgentLLMClient(
            agent_name="Therapist",
            system_prompt=THERAPIST_SYSTEM_PROMPT
        )
        
        # Initialize interview orchestrator for guided questions
        try:
            from app.agents.interview import InterviewOrchestrator
            self.interview_orchestrator = InterviewOrchestrator(llm_client=self.llm_client)
            self.use_guided_interview = True
        except Exception as e:
            self.interview_orchestrator = None
            self.use_guided_interview = False
    
    async def process(self, state: Dict) -> AgentOutput:
        """
        Process user message and generate therapeutic response.
        
        Args:
            state: Current conversation state containing:
                - messages: List of conversation messages
                - symptoms: Extracted symptoms from SRA
                - user_message: Latest user input
                - session_id: Session identifier
        
        Returns:
            AgentOutput with therapist response and metadata
        """
        try:
            user_message = state.get("user_message", "")
            messages = state.get("messages", [])
            symptoms = state.get("symptoms", [])
            
            # Determine conversation phase
            phase = self.techniques.determine_phase(
                message_count=len(messages),
                symptom_count=len(symptoms),
                has_deep_exploration=self._has_deep_exploration(messages)
            )
            
            # Check for risk indicators
            risk_level = self.techniques.detect_risk_keywords(user_message)
            
            # Handle high-risk situations specially
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                return await self._handle_safety_concern(state, risk_level)
            
            # Generate appropriate response based on phase
            if len(messages) == 0:
                response = await self._generate_greeting()
            else:
                response = await self._generate_response(
                    user_message=user_message,
                    state=state,
                    phase=phase
                )
            
            return AgentOutput(
                content=response,
                metadata={
                    "phase": phase.value,
                    "risk_level": risk_level.value,
                    "message_count": len(messages) + 1,
                    "symptom_count": len(symptoms),
                }
            )
            
        except Exception as e:
            self.log_error(f"Error processing message: {e}", exc_info=True)
            return AgentOutput(
                content=self._get_fallback_response(),
                error=str(e)
            )
    
    async def _generate_greeting(self) -> str:
        """Generate warm opening greeting"""
        try:
            response = await self.llm_client.generate_async(GREETING_PROMPT)
            return response
        except Exception as e:
            self.log_error(f"Error generating greeting: {e}")
            return (
                "Hello, and welcome. I'm here to listen and understand "
                "what you're going through. Everything you share stays "
                "confidential. How are you feeling today?"
            )
    
    async def _generate_response(
        self,
        user_message: str,
        state: Dict,
        phase: ConversationPhase
    ) -> str:
        """Generate contextual therapeutic response with SCID-guided questioning"""
        
        # Build context for LLM
        symptoms = state.get("symptoms", [])
        topics = self._extract_topics(state.get("messages", []))
        session_id = state.get("session_id")
        patient_id = state.get("patient_id", "")
        
        # Get guided question from interview orchestrator if available
        guided_question = None
        if self.use_guided_interview and self.interview_orchestrator and session_id:
            try:
                interview_step = await self.interview_orchestrator.get_next_step(
                    session_id=session_id,
                    patient_id=patient_id,
                    user_message=user_message
                )
                
                if interview_step.get("action") == "ask_question":
                    guided_question = interview_step.get("question_text")
                    state["_interview_step"] = interview_step  # Store for reference
            except Exception as e:
                self.log_error(f"Interview orchestrator error: {e}")
        
        # Build prompt with guided question context
        if guided_question:
            prompt = f"""Based on the patient's response, generate a natural, empathetic follow-up.

Patient said: {user_message}

Current context:
- Topics discussed: {", ".join(topics) if topics else "none yet"}
- Symptoms mentioned: {", ".join([s.get("name", "") for s in symptoms[:5]]) if symptoms else "none yet"}
- Conversation phase: {phase.value}

IMPORTANT: You must ask this clinical question in a natural, conversational way:
"{guided_question}"

Your response should:
1. First acknowledge what they shared (1 sentence)
2. Then naturally transition to the guided question
3. Keep the tone warm and empathetic

Response (2-4 sentences):"""
        else:
            prompt = FOLLOW_UP_PROMPT.format(
                user_message=user_message,
                topics=", ".join(topics) if topics else "none yet",
                symptoms=", ".join([s.get("name", "") for s in symptoms[:5]]) if symptoms else "none yet",
                phase=phase.value
            )
        
        try:
            response = await self.llm_client.generate_async(prompt)
            return response
        except Exception as e:
            self.log_error(f"Error generating response: {e}")
            return self._get_fallback_response()
    
    async def _handle_safety_concern(
        self,
        state: Dict,
        risk_level: RiskLevel
    ) -> AgentOutput:
        """Handle high-risk safety concerns with appropriate response"""
        
        self.log_info(f"Safety concern detected: {risk_level.value}")
        
        safety_responses = self.techniques.safety_responses()
        response = safety_responses[0]  # Primary safety response
        
        return AgentOutput(
            content=response,
            metadata={
                "phase": "safety",
                "risk_level": risk_level.value,
                "requires_escalation": risk_level == RiskLevel.CRITICAL,
            }
        )
    
    def _has_deep_exploration(self, messages: List[Dict]) -> bool:
        """Check if conversation has deep exploration markers"""
        deep_markers = ["how often", "how long", "when did", "intensity", "triggers"]
        
        for msg in messages:
            content = msg.get("content", "").lower()
            if any(marker in content for marker in deep_markers):
                return True
        return False
    
    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """Extract discussed topics from conversation history"""
        topics = set()
        topic_keywords = [
            "sleep", "anxiety", "depression", "stress", "work",
            "relationship", "family", "mood", "energy", "appetite"
        ]
        
        for msg in messages:
            content = msg.get("content", "").lower()
            for keyword in topic_keywords:
                if keyword in content:
                    topics.add(keyword)
        
        return list(topics)
    
    def _get_fallback_response(self) -> str:
        """Fallback response when LLM fails"""
        fallbacks = [
            "I hear you. Can you tell me more about that?",
            "Thank you for sharing. How has this been affecting you?",
            "That sounds difficult. What's been on your mind lately?",
        ]
        import random
        return random.choice(fallbacks)


__all__ = ["TherapistAgent"]
