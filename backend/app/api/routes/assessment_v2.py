"""
Assessment API Routes V2
========================
Optimized routes using the new agent architecture.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

router = APIRouter(prefix="/v2/assessment", tags=["assessment-v2"])


class StartSessionRequest(BaseModel):
    patient_id: str


class MessageRequest(BaseModel):
    session_id: str
    patient_id: str
    message: str


class SessionResponse(BaseModel):
    session_id: str
    response: str
    phase: str
    symptom_count: int = 0
    diagnosis_ready: bool = False


class DiagnosisResponse(BaseModel):
    primary: Optional[Dict] = None
    differentials: List[Dict] = []
    clinical_report: Optional[str] = None
    symptom_count: int = 0


class StateResponse(BaseModel):
    session_id: str
    patient_id: str
    phase: str
    message_count: int
    symptom_count: int
    symptoms: List[Dict]
    diagnosis_ready: bool
    risk_level: str


@router.post("/start", response_model=SessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new assessment session"""
    from app.agents.orchestrator import get_orchestrator
    import uuid
    
    session_id = str(uuid.uuid4())
    orchestrator = get_orchestrator()
    
    result = await orchestrator.start_session(session_id, request.patient_id)
    
    return SessionResponse(
        session_id=session_id,
        response=result["response"],
        phase=result.get("phase", "rapport")
    )


@router.post("/message", response_model=SessionResponse)
async def process_message(request: MessageRequest):
    """Process a user message in the assessment"""
    from app.agents.orchestrator import get_orchestrator
    
    orchestrator = get_orchestrator()
    
    result = await orchestrator.process_message(
        session_id=request.session_id,
        patient_id=request.patient_id,
        user_message=request.message
    )
    
    return SessionResponse(
        session_id=request.session_id,
        response=result["response"],
        phase=result.get("phase", "exploration"),
        symptom_count=result.get("symptom_count", 0),
        diagnosis_ready=result.get("diagnosis_ready", False)
    )


@router.get("/diagnosis/{session_id}", response_model=DiagnosisResponse)
async def get_diagnosis(session_id: str):
    """Get diagnosis for a session"""
    from app.agents.orchestrator import get_orchestrator
    
    orchestrator = get_orchestrator()
    result = await orchestrator.get_diagnosis(session_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Session not found or diagnosis not ready")
    
    return DiagnosisResponse(
        primary=result.get("primary_diagnosis"),
        differentials=result.get("differential_diagnoses", []),
        clinical_report=result.get("clinical_report"),
        symptom_count=result.get("symptom_count", 0)
    )


@router.get("/state/{session_id}", response_model=StateResponse)
async def get_session_state(session_id: str):
    """Get current session state"""
    from app.agents.orchestrator import get_orchestrator
    
    orchestrator = get_orchestrator()
    state = orchestrator.get_session_state(session_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return StateResponse(**state)


@router.get("/tools")
async def list_registered_tools():
    """List all registered MCP tools"""
    from app.agents.core import get_registry
    
    registry = get_registry()
    return {"tools": registry.list_tools()}


__all__ = ["router"]
