from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from uuid import UUID

from app.models.enums import AdminRoleEnum, AccountStatusEnum

class AdminBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    role: AdminRoleEnum = AdminRoleEnum.ADMIN

class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)

class AdminUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    role: Optional[AdminRoleEnum] = None
    status: Optional[AccountStatusEnum] = None

class AdminResponse(AdminBase):
    id: UUID
    status: AccountStatusEnum
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
