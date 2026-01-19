"""
Assessment Schemas
==================
Pydantic models for assessment API endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AssessmentChatRequest(BaseModel):
    """Request model for sending a message"""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Existing session ID")

class AssessmentChatResponse(BaseModel):
    """Response model for chat interaction"""
    session_id: str
    response: str
    is_complete: bool = False
    current_phase: Optional[str] = None
    risk_level: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StartSessionResponse(BaseModel):
    """Response model for starting a session"""
    session_id: str
    greeting: str
    started_at: datetime
    patient_id: str

class ConversationMessageSchema(BaseModel):
    """Schema for a single conversation message"""
    role: str
    content: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SessionHistoryResponse(BaseModel):
    """Response model for session history"""
    session_id: str
    messages: List[ConversationMessageSchema]
    total_messages: int
