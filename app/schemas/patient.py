from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import date
from typing import Optional
from uuid import UUID

from app.models.enums import GenderEnum, AccountStatusEnum

class PatientBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    date_of_birth: date
    gender: GenderEnum
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field("Pakistan", max_length=100)

class PatientCreate(PatientBase):
    password: str = Field(..., min_length=8)

class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)

class PatientResponse(PatientBase):
    """Full response — only shown to the patient themselves or an admin."""
    id: UUID
    account_status: AccountStatusEnum
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class PatientSpecialistView(BaseModel):
    """
    Limited view of a patient — returned to an associated specialist.
    Excludes personal/sensitive fields: email, phone, date_of_birth.
    """
    id: UUID
    first_name: str
    last_name: str
    gender: GenderEnum
    city: Optional[str] = None
    country: Optional[str] = None
    account_status: AccountStatusEnum

    model_config = ConfigDict(from_attributes=True)


class AssessmentSessionBase(BaseModel):
    session_id: str
    is_completed: bool = False
    symptoms: Optional[dict | list] = None
    conversation_history: Optional[dict | list] = None
    clinical_report: Optional[dict | str] = None
    diagnoser_results: Optional[dict | list] = None
    treatment_plan: Optional[dict | str] = None
    recommended_specialists: Optional[dict] = None

class AssessmentSessionCreate(AssessmentSessionBase):
    patient_id: UUID

class AssessmentSessionResponse(AssessmentSessionBase):
    id: UUID
    patient_id: UUID

    model_config = ConfigDict(from_attributes=True)
