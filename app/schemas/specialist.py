from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.enums import (
    GenderEnum, SpecialistTypeEnum, AvailabilityStatusEnum,
    ApprovalStatusEnum, AccountStatusEnum
)

class SpecialistBase(BaseModel):
    """Shared properties across all specialist schemas."""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    cnic_number: Optional[str] = Field(None, max_length=15)
    gender: Optional[GenderEnum] = None
    specialist_type: Optional[SpecialistTypeEnum] = None
    years_experience: Optional[int] = Field(0, ge=0)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field("Pakistan", max_length=100)
    address: Optional[str] = None
    clinic_name: Optional[str] = Field(None, max_length=200)
    consultation_fee: Optional[float] = Field(None, ge=0)
    bio: Optional[str] = None
    languages_spoken: Optional[List[str]] = None

class SpecialistCreate(SpecialistBase):
    """Model used for specialist registration."""
    password: str = Field(..., min_length=8)

class SpecialistUpdate(BaseModel):
    """Model used for updating specialist profile."""
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    clinic_name: Optional[str] = Field(None, max_length=200)
    consultation_fee: Optional[float] = Field(None, ge=0)
    bio: Optional[str] = None
    availability_status: Optional[AvailabilityStatusEnum] = None

    # JSON array updates
    education_records: Optional[List[Dict[str, Any]]] = None
    experience_records: Optional[List[Dict[str, Any]]] = None
    specialties_in_mental_health: Optional[List[str]] = None
    therapy_methods: Optional[List[str]] = None
    documents: Optional[List[str]] = None


# ──────────────────────────────────────────────
# Response schemas (layered by visibility level)
# ──────────────────────────────────────────────

class SpecialistListResponse(BaseModel):
    """
    Minimal public card — used for GET /specialists/ directory listing.
    No contact details. Enough for a patient to browse and pick a specialist.
    """
    id: UUID
    first_name: str
    last_name: str
    specialist_type: Optional[SpecialistTypeEnum] = None
    years_experience: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    clinic_name: Optional[str] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    availability_status: AvailabilityStatusEnum
    is_verified: bool
    specialties_in_mental_health: Optional[List[str]] = None
    therapy_methods: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class SpecialistDetailResponse(BaseModel):
    """
    Full profile — returned only to the specialist themselves or an admin.
    Includes sensitive contact info: phone, CNIC, address.
    """
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    cnic_number: Optional[str] = None
    gender: Optional[GenderEnum] = None
    specialist_type: Optional[SpecialistTypeEnum] = None
    years_experience: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    clinic_name: Optional[str] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    languages_spoken: Optional[List[str]] = None
    availability_status: AvailabilityStatusEnum
    approval_status: ApprovalStatusEnum
    account_status: AccountStatusEnum
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    education_records: Optional[List[Dict[str, Any]]] = None
    experience_records: Optional[List[Dict[str, Any]]] = None
    specialties_in_mental_health: Optional[List[str]] = None
    therapy_methods: Optional[List[str]] = None
    documents: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


# Keep SpecialistResponse as alias for internal / admin use
SpecialistResponse = SpecialistDetailResponse
