from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from app.models.enums import AppointmentStatusEnum, ConsultationModeEnum

class AppointmentBase(BaseModel):
    scheduled_at: datetime
    duration_minutes: int = 60
    appointment_type: ConsultationModeEnum = ConsultationModeEnum.ONLINE
    reason: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    specialist_id: UUID
    assessment_session_id: Optional[UUID] = None

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatusEnum] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    meeting_link: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: UUID
    patient_id: UUID
    specialist_id: UUID
    assessment_session_id: Optional[UUID] = None
    status: AppointmentStatusEnum
    meeting_link: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AppointmentListResponse(BaseModel):
    appointments: List[AppointmentResponse]
    total: int
