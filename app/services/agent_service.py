import logging
from uuid import UUID
from typing import Optional, AsyncGenerator

from app.agents.graph import get_mindmate_graph
from app.agents.state import MindMateState
from app.services.streaming_service import StreamingService
from app.services.assessment_service import AssessmentService
from app.models.patient import Patient
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

class AgentService:
    @staticmethod
    async def get_or_create_session_id(db: Session, patient_id: UUID, session_id: Optional[str] = None) -> str:
        """Ensures a session ID exists, creating one if necessary."""
        import uuid
        if not session_id:
            return f"sess_{uuid.uuid4().hex[:12]}"
        return session_id

    @staticmethod
    async def chat_stream(
        db: Session, 
        patient: Patient, 
        message: str, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Executes the agent graph and streams the response.
        """
        graph = await get_mindmate_graph()
        
        # 1. Prepare initial state
        config = {"configurable": {"thread_id": session_id}}
        
        # 2. Add message to state
        # LangGraph automatically handles history via checkpointer
        input_state = {
            "messages": [HumanMessage(content=message)],
            "patient_id": str(patient.id),
            "patient_context": {
                "gender": patient.gender.value if patient.gender else "unknown",
                "city": patient.city or "unknown",
                "age": "unknown"  # Could calculate from DOB
            }
        }

        # 3. Stream from graph
        async for chunk in StreamingService.stream_events(graph, input_state, config):
            yield chunk

        # 4. Save progress automatically using AssessmentService
        try:
            # Refresh context to get final state
            final_state = await graph.aget_state(config)
            if final_state and final_state.values:
                AssessmentService.save_session_progress(
                    session_id=session_id, 
                    state=final_state.values
                )
        except Exception as e:
            logger.error(f"Error saving agent progress: {e}")
