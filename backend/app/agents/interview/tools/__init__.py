"""
Interview MCP Tools
===================
MCP-style tools for the Interview Orchestrator.
"""

from typing import Dict, List, Any

# Tool schemas for MCP registration
TOOLS = {
    "get_next_interview_step": {
        "name": "get_next_interview_step",
        "description": "Get the next step in the SCID interview based on current state",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "patient_id": {"type": "string"},
                "user_message": {"type": "string", "description": "User's response to previous question"}
            },
            "required": ["session_id", "patient_id"]
        }
    },
    "get_screening_items": {
        "name": "get_screening_items",
        "description": "Get relevant SCID-SC screening items based on demographics and concerns",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "demographics": {"type": "object"},
                "presenting_concerns": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["session_id"]
        }
    },
    "evaluate_screening_response": {
        "name": "evaluate_screening_response",
        "description": "Evaluate user response to a screening question",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question_id": {"type": "string"},
                "response": {"type": "string"},
                "context": {"type": "object"}
            },
            "required": ["question_id", "response"]
        }
    },
    "get_module_to_deploy": {
        "name": "get_module_to_deploy",
        "description": "Determine which SCID-CV module to deploy next based on positive screens",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "positive_screens": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["session_id", "positive_screens"]
        }
    },
    "format_question_naturally": {
        "name": "format_question_naturally",
        "description": "Format a clinical question in a natural, conversational way",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question_text": {"type": "string"},
                "context": {"type": "object"},
                "previous_response": {"type": "string"}
            },
            "required": ["question_text"]
        }
    }
}


async def get_next_interview_step(
    session_id: str,
    patient_id: str,
    user_message: str = "",
    orchestrator=None
) -> Dict[str, Any]:
    """Get next interview step from orchestrator"""
    if orchestrator:
        return await orchestrator.get_next_step(session_id, patient_id, user_message)
    return {"error": "Orchestrator not initialized"}


async def evaluate_screening_response(
    question_id: str,
    response: str,
    context: Dict = None,
    llm_client=None
) -> Dict[str, Any]:
    """Evaluate a screening response using LLM or rules"""
    
    # Simple keyword detection
    positive_keywords = ["yes", "yeah", "definitely", "i have", "i do", "that's right"]
    negative_keywords = ["no", "not", "never", "haven't", "don't"]
    
    response_lower = response.lower()
    
    positive_count = sum(1 for kw in positive_keywords if kw in response_lower)
    negative_count = sum(1 for kw in negative_keywords if kw in response_lower)
    
    is_positive = positive_count > negative_count
    confidence = abs(positive_count - negative_count) / max(1, positive_count + negative_count)
    
    return {
        "question_id": question_id,
        "is_positive": is_positive,
        "confidence": confidence,
        "needs_clarification": confidence < 0.3
    }


async def format_question_naturally(
    question_text: str,
    context: Dict = None,
    previous_response: str = "",
    llm_client=None
) -> str:
    """Format a clinical question naturally"""
    
    if llm_client:
        try:
            prompt = f"""Rephrase this clinical question to sound natural and conversational, 
while maintaining its clinical accuracy. Keep it brief.

Original question: {question_text}
{"Previous user response: " + previous_response if previous_response else ""}

Natural version (one sentence):"""
            
            response = await llm_client.generate_async(
                prompt=prompt,
                temperature=0.3,
                max_tokens=100
            )
            return response.strip()
        except Exception:
            pass
    
    # Fallback: Return as-is
    return question_text


def list_tools() -> List[Dict]:
    """List all available tools"""
    return [{"name": name, "schema": schema} for name, schema in TOOLS.items()]


def get_tool(name: str) -> Dict:
    """Get tool by name"""
    return TOOLS.get(name)


__all__ = [
    "TOOLS",
    "get_next_interview_step",
    "evaluate_screening_response",
    "format_question_naturally",
    "list_tools",
    "get_tool"
]
