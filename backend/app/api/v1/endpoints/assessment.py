"""
Assessment API (Refactored)
===========================
Streamlined assessment workflow using Therapist Agent and Repositories.
"""

import logging
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_patient
from app.models_new import Patient, AssessmentSession, SessionStatus
from app.db.repositories_new import assessment_repo
from app.schemas.assessment import (
    AssessmentChatRequest,
    AssessmentChatResponse,
    StartSessionResponse,
    SessionHistoryResponse,
    ConversationMessageSchema
)

from app.agents.sra.agent import SymptomRecognitionAgent
from app.agents.therapist.agent import TherapistAgent
from app.agents.diagnosis.agent import DiagnosisAgent
from app.agents.matcher.agent import MatcherAgent

# Initialize Router
router = APIRouter(prefix="/assessment", tags=["Assessment"])
logger = logging.getLogger(__name__)

# Initialize Agents
try:
    therapist_agent = TherapistAgent()
    sra_agent = SymptomRecognitionAgent(llm_client=therapist_agent.llm_client)
    diagnosis_agent = DiagnosisAgent(llm_client=therapist_agent.llm_client)
    matcher_agent = MatcherAgent()
except Exception as e:
    logger.error(f"Failed to initialize Agents: {e}")
    raise e


@router.post("/diagnose", response_model=Any)
async def trigger_diagnosis(
    request: AssessmentChatRequest, # Reusing schema for session_id
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
) -> Any:
    """
    Trigger diagnostic analysis for a session.
    """
    session_id = request.session_id
    if not session_id:
         raise HTTPException(status_code=400, detail="Session ID required")
         
    # Run Diagnosis Agent
    try:
        agent_output = await diagnosis_agent.process({
            "session_id": session_id,
            "patient_id": current_patient.id,
            "symptoms": [] # Agent will fetch from DB
        })
        return agent_output.content
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match", response_model=Any)
async def trigger_matching(
    request: AssessmentChatRequest,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
) -> Any:
    """
    Trigger specialist matching for a session (after diagnosis).
    """
    session_id = request.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    try:
        agent_output = await matcher_agent.process({
            "session_id": session_id,
            "patient_id": str(current_patient.id)
        })
        return agent_output.content
    except Exception as e:
        logger.error(f"Matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matches/{session_id}", response_model=Any)
def get_matches(
    session_id: str,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
) -> Any:
    """
    Get stored specialist matches for a session.
    """
    matches = assessment_repo.get_matches(db, session_id)
    return {
        "matches": [
            {
                "specialist_id": str(m.specialist_id),
                "match_score": float(m.match_score),
                "rank": m.rank,
                "reasons": m.match_reasons,
                "selected": m.selected
            }
            for m in matches
        ],
        "total": len(matches)
    }


@router.post("/start", response_model=StartSessionResponse)
def start_session(
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
) -> Any:
    """
    Start a new assessment session.
    """
    # 1. Create Session in DB
    session = AssessmentSession(
        patient_id=current_patient.id,
        status=SessionStatus.ACTIVE
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # 2. Get Agent Greeting (Mocking async call or running sync)
    import asyncio
    try:
        greeting = asyncio.run(therapist_agent._generate_greeting())
    except Exception as e:
        logger.error(f"Failed to generate greeting: {e}")
        greeting = "Hello. I'm here to help you understand what you're going through. How can I help you today?"
        
    # 3. Store Greeting
    assessment_repo.add_message(
        db, 
        session_id=session.id, 
        role="assistant", 
        content=greeting
    )
    
    return StartSessionResponse(
        session_id=str(session.id),
        greeting=greeting,
        started_at=session.started_at,
        patient_id=str(current_patient.id)
    )


@router.post("/chat", response_model=AssessmentChatResponse)
async def chat(
    request: AssessmentChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
) -> Any:
    """
    Send a message to the therapist agent.
    """
    session_id = request.session_id
    
    # 1. Validate Session
    if not session_id:
        # Auto-create if not provided? For now enforce start or provide ID
        # Let's auto-create for better UX if missing
        session = AssessmentSession(
            patient_id=current_patient.id,
            status=SessionStatus.ACTIVE
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = str(session.id)
    else:
        session = assessment_repo.get(db, id=session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if str(session.patient_id) != str(current_patient.id):
             raise HTTPException(status_code=403, detail="Not authorized for this session")

    # 2. Store User Message
    assessment_repo.add_message(
        db,
        session_id=session_id,
        role="user",
        content=request.message
    )
    
    # 3. Trigger SRA in Background
    async def run_sra(s_id, msg):
        try:
            await sra_agent.process({
                "session_id": s_id,
                "user_message": msg
            })
        except Exception as e:
            logger.error(f"Background SRA failed: {e}")

    background_tasks.add_task(run_sra, session_id, request.message)

    # 4. Build Agent State
    # Fetch history
    history = assessment_repo.get_conversation_history(db, session_id)
    messages_dicts = [
        {"role": msg.role, "content": msg.content} 
        for msg in history
    ]
    
    # Fetch Symptoms from DB for context
    symptoms_objs = assessment_repo.get_symptoms(db, session_id)
    symptoms = [
        {"name": s.symptom_name, "severity": float(s.severity), "category": s.category} 
        for s in symptoms_objs
    ]
    
    agent_state = {
        "messages": messages_dicts,
        "user_message": request.message,
        "symptoms": symptoms,
        "session_id": session_id
    }
    
    # 5. Run Agent
    try:
        agent_output = await therapist_agent.process(agent_state)
        response_text = agent_output.content
        metadata = agent_output.metadata or {}
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        response_text = "I apologize, but I'm having trouble processing that right now. Could you rephrase?"
        metadata = {"error": str(e)}

    # 6. Store Assistant Response
    assessment_repo.add_message(
        db,
        session_id=session_id,
        role="assistant",
        content=response_text,
        metadata=metadata
    )
    
    return AssessmentChatResponse(
        session_id=session_id,
        response=response_text,
        metadata=metadata
    )


@router.get("/history/{session_id}", response_model=SessionHistoryResponse)
def get_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
) -> Any:
    """
    Get conversation history.
    """
    session = assessment_repo.get(db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if str(session.patient_id) != str(current_patient.id):
            raise HTTPException(status_code=403, detail="Not authorized")
            
    messages = assessment_repo.get_conversation_history(db, session_id)
    
    return SessionHistoryResponse(
        session_id=session_id,
        messages=[
            ConversationMessageSchema(
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                metadata=msg.msg_metadata or {}
            )
            for msg in messages
        ],
        total_messages=len(messages)
    )

@router.get("/session/active", response_model=StartSessionResponse)
def get_active_session(
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
) -> Any:
    """
    Get current active session if exists.
    """
    session = assessment_repo.get_active_session(db, current_patient.id)
    if not session:
         raise HTTPException(status_code=404, detail="No active session found")
         
    # Get last message as 'greeting' placeholder or system status
    last_msg = ""
    messages = assessment_repo.get_conversation_history(db, session.id)
    if messages:
        last_msg = messages[-1].content
        
    return StartSessionResponse(
        session_id=str(session.id),
        greeting=last_msg, # placeholder
        started_at=session.started_at,
        patient_id=str(session.patient_id)
    )
