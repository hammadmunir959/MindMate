from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1 import deps
from app.schemas.agent_schemas import ChatRequest
from app.services.agent_service import AgentService
from app.models.patient import Patient

router = APIRouter()

@router.post("/chat")
async def chat_with_agent(
    *,
    db: Session = Depends(deps.get_db),
    current_patient: Patient = Depends(deps.get_current_patient),
    request: ChatRequest
) -> Any:
    """
    Streaming endpoint for chatting with the MindMate clinical agent.
    """
    session_id = await AgentService.get_or_create_session_id(
        db, current_patient.id, request.session_id
    )

    return StreamingResponse(
        AgentService.chat_stream(
            db=db,
            patient=current_patient,
            message=request.message,
            session_id=session_id
        ),
        media_type="text/event-stream"
    )
