from sqlalchemy import Column, Integer, String, Boolean, Enum
from .base import Base, BaseModel
from .enums import AdminRoleEnum, AccountStatusEnum, USERTYPE

class Admin(Base, BaseModel):
    """Core admin model"""
    __tablename__ = "admins"
    
    # Basic Information
    user_type = Column(Enum(USERTYPE), nullable=False, default=USERTYPE.ADMIN)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Admin roles and status
    role = Column(Enum(AdminRoleEnum), nullable=False, default=AdminRoleEnum.ADMIN)
    status = Column(Enum(AccountStatusEnum), nullable=False, default=AccountStatusEnum.ACTIVE)
    
    # Authentication & Security
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
