"""
Optimized Therapist Agent V2
============================
Natural, SCID-guided therapeutic conversations.
Uses MCP tools for interview guidance.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging

from app.agents.base import BaseAgent, AgentOutput
from app.agents.core import (
    ConversationState, ConversationPhase, RiskLevel,
    Symptom, get_state_manager, get_registry, register_tool
)
from app.core.llm_client import AgentLLMClient

logger = logging.getLogger(__name__)


# =============================================================================
# MCP TOOLS
# =============================================================================

@register_tool(
    name="get_guided_question",
    description="Get next SCID-guided question based on conversation state",
    input_schema={
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
            "symptoms": {"type": "array"},
            "phase": {"type": "string"}
        },
        "required": ["session_id"]
    },
    agent="therapist"
)
async def get_guided_question(session_id: str, symptoms: List = None, phase: str = None) -> Dict:
    """Get next question from interview orchestrator"""
    try:
        from app.agents.interview import InterviewOrchestrator
        orchestrator = InterviewOrchestrator()
        state = get_state_manager().get(session_id)
        patient_id = state.patient_id if state else ""
        
        return await orchestrator.get_next_step(session_id, patient_id, "")
    except Exception as e:
        logger.warning(f"Could not get guided question: {e}")
        return {"question_text": None}


@register_tool(
    name="detect_risk",
    description="Detect risk indicators in user message",
    input_schema={
        "type": "object",
        "properties": {
            "message": {"type": "string"}
        },
        "required": ["message"]
    },
    agent="therapist"
)
def detect_risk(message: str) -> Dict:
    """Detect risk indicators in message"""
    risk_keywords = {
        RiskLevel.CRITICAL: ["suicide", "kill myself", "end my life", "want to die", "better off dead", "sleep forever", "never wake up", "gun", "weapon", "loading it", "hanging", "overdose"],
        RiskLevel.HIGH: ["hurt myself", "self-harm", "cutting", "don't want to live", "no reason to live", "wish i was dead", "not want to live"],
        RiskLevel.MODERATE: ["hopeless", "worthless", "can't go on", "give up", "nothing matters", "hate my life"]
    }
    
    message_lower = message.lower()
    
    for level, keywords in risk_keywords.items():
        if any(kw in message_lower for kw in keywords):
            return {"risk_level": level.value, "detected": True}
    
    return {"risk_level": RiskLevel.NONE.value, "detected": False}


@register_tool(
    name="determine_phase",
    description="Determine conversation phase based on message count and symptoms",
    input_schema={
        "type": "object",
        "properties": {
            "message_count": {"type": "integer"},
            "symptom_count": {"type": "integer"}
        },
        "required": ["message_count", "symptom_count"]
    },
    agent="therapist"
)
def determine_phase(message_count: int, symptom_count: int) -> str:
    """Determine conversation phase"""
    if message_count <= 4:
        return ConversationPhase.RAPPORT.value
    elif symptom_count >= 3 and message_count >= 10:
        return ConversationPhase.DEEPENING.value
    elif message_count >= 15:
        return ConversationPhase.CLOSING.value
    else:
        return ConversationPhase.EXPLORATION.value


# =============================================================================
# PROMPTS
# =============================================================================

SYSTEM_PROMPT = """You are MindMate, a warm and empathetic AI mental health assistant.

CORE PRINCIPLES:
1. Be warm, non-judgmental, genuinely curious
2. Use active listening - reflect back what you hear
3. Ask open-ended questions that invite sharing
4. Validate emotions before exploring further
5. Guide gently, don't interrogate
6. Keep responses concise (2-4 sentences)

PHASE-SPECIFIC BEHAVIOR:
- RAPPORT: Warm welcome, build trust, open-ended questions
- EXPLORATION: Follow patient's lead, clarify, explore concerns
- DEEPENING: Frequency, duration, impact, triggers
- CLOSING: Summarize, next steps, reassurance

CURRENT CONTEXT:
- Phase: {phase}
- Topics: {topics}
- Symptoms found: {symptom_count}
- Risk level: {risk_level}
"""

GUIDED_QUESTION_PROMPT = """You are conducting a structured clinical assessment but must remain warm and natural.

Patient said: "{user_message}"

MANDATORY CLINICAL QUESTION:
"{guided_question}"

INSTRUCTIONS:
1. Acknowledge and validate the patient's last message (1 sentence).
2. Transition naturally to the MANDATORY CLINICAL QUESTION.
3. You MUST ask the clinical question, preservering its core criteria (timeframes, specific symptoms).
4. Do NOT simply append it robotically. Weave it into the conversation flow.
5. Keep the total response to 3-4 sentences.

Example:
Patient: "I just feel so tired all the time."
Question: "Have you had trouble sleeping properly?"
Response: "It sounds exhausting to feel that drained every day. Has this tiredness been linked to any trouble sleeping properly at night?"

Response:"""

# Deterministic safety responses (No LLM generation for safety)
SAFETY_RESPONSES = {
    RiskLevel.CRITICAL: (
        "I'm hearing how much pain you're in right now, and I'm concerned about your safety. "
        "Please, I want you to be safe. If you are in immediate danger, please call emergency services "
        "or go to the nearest emergency room immediately. Can you tell me you're safe right now?"
    ),
    RiskLevel.HIGH: (
        "It sounds like you're going through an incredibly difficult time, and I want to make sure you have support. "
        "You don't have to go through this alone. Have you shared these feelings with a professional or a trusted person in your life?"
    )
}


# =============================================================================
# AGENT
# =============================================================================

class TherapistAgentV2(BaseAgent):
    """
    Optimized Therapist Agent V2.1
    
    Features:
    - SCID-guided questioning (Natural Constraint-Based)
    - Deterministic Safety Override
    - 4-phase conversation flow
    - Integration with state manager
    """
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="TherapistAgentV2", **kwargs)
        self.llm_client = AgentLLMClient(
            agent_name="Therapist",
            system_prompt=SYSTEM_PROMPT
        )
        self.state_manager = get_state_manager()
        self.tool_registry = get_registry()
    
    async def process(self, state: Dict) -> AgentOutput:
        """Process user message and generate therapeutic response"""
        
        session_id = state.get("session_id")
        patient_id = state.get("patient_id", "")
        user_message = state.get("user_message", "")
        
        # Get or create conversation state
        conv_state = self.state_manager.get_or_create(session_id, patient_id)
        
        # Add user message to history
        conv_state.add_message("user", user_message)
        
        try:
            # 1. Check for risk (Deterministic Priority)
            risk_result = detect_risk(user_message)
            if risk_result["detected"]:
                level = RiskLevel(risk_result["risk_level"])
                conv_state.risk_level = level
                
                # Deterministic Safety Override for High/Critical
                if level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                    response = SAFETY_RESPONSES.get(level, SAFETY_RESPONSES[RiskLevel.HIGH])
                    conv_state.add_message("assistant", response)
                    self.state_manager.save(conv_state)
                    return AgentOutput(
                        content=response,
                        metadata={"phase": "safety", "risk_level": level.value}
                    )
            
            # 2. Determine phase
            phase = determine_phase(
                message_count=len(conv_state.messages),
                symptom_count=len(conv_state.symptoms)
            )
            conv_state.phase = ConversationPhase(phase)
            
            # 3. Get guided question if available
            guided_question = None
            try:
                # Need to run in executor or await if async compatible (orchestrator is async)
                # But here we call the tool wrapper which returns a dict
                guided_result = await get_guided_question(
                    session_id=session_id,
                    symptoms=[s.name for s in conv_state.symptoms],
                    phase=phase
                )
                if guided_result.get("action") == "ask_question":
                    guided_question = guided_result.get("question_text")
            except Exception as e:
                logger.debug(f"No guided question: {e}")
            
            # 4. Generate response
            if len(conv_state.messages) <= 2:
                response = await self._generate_greeting()
            elif guided_question:
                response = await self._generate_guided_response(user_message, guided_question)
            else:
                response = await self._generate_response(user_message, conv_state)
            
            # 5. Update state
            conv_state.add_message("assistant", response)
            self.state_manager.save(conv_state)
            
            return AgentOutput(
                content=response,
                metadata={
                    "phase": phase,
                    "symptom_count": len(conv_state.symptoms),
                    "risk_level": conv_state.risk_level.value,
                    "message_count": len(conv_state.messages)
                }
            )
            
        except Exception as e:
            logger.error(f"Therapist error: {e}", exc_info=True)
            fallback = self._get_fallback_response()
            conv_state.add_message("assistant", fallback)
            self.state_manager.save(conv_state)
            return AgentOutput(content=fallback, error=str(e))
    
    async def _generate_greeting(self) -> str:
        """Generate warm greeting"""
        try:
            prompt = """Generate a warm, welcoming greeting for a mental health conversation.
Keep it to 2-3 sentences. Be warm and reassuring."""
            return await self.llm_client.generate_async(prompt)
        except Exception:
            return (
                "Hello, and welcome. I'm here to listen and understand what you're going through. "
                "Everything you share stays confidential. How are you feeling today?"
            )
    
    async def _generate_guided_response(self, user_message: str, guided_question: str) -> str:
        """Generate response incorporating guided question naturally"""
        prompt = GUIDED_QUESTION_PROMPT.format(
            user_message=user_message,
            guided_question=guided_question
        )
        try:
            return await self.llm_client.generate_async(prompt)
        except Exception:
            # Fallback: simple bridge
            return f"I understand. {guided_question}"
    
    async def _generate_response(self, user_message: str, conv_state: ConversationState) -> str:
        """Generate context-aware response"""
        prompt = f"""Based on the patient's response, generate a follow-up.

Patient said: {user_message}

Context:
- Phase: {conv_state.phase.value}
- Topics: {', '.join(conv_state.active_topics) if conv_state.active_topics else 'none yet'}
- Symptoms: {len(conv_state.symptoms)}

Response (2-4 sentences, warm and empathetic):"""
        
        try:
            return await self.llm_client.generate_async(prompt)
        except Exception:
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback when LLM fails"""
        import random
        fallbacks = [
            "I hear you. Can you tell me more about that?",
            "Thank you for sharing. How has this been affecting you?",
            "That sounds difficult. What's been on your mind lately?"
        ]
        return random.choice(fallbacks)


__all__ = ["TherapistAgentV2"]
