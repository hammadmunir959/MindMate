from sqlalchemy import Column, String, Boolean, Enum, JSON, Integer, Numeric, Text, DateTime
from datetime import datetime
from .base import Base, BaseModel
from .enums import USERTYPE, GenderEnum, SpecialistTypeEnum, AvailabilityStatusEnum, ApprovalStatusEnum, AccountStatusEnum

class Specialist(Base, BaseModel):
    """Core specialist model including authentication"""
    __tablename__ = "specialists"

    user_type = Column(Enum(USERTYPE), nullable=False, default=USERTYPE.SPECIALIST)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    cnic_number = Column(String(15), nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    
    # Authentication
    hashed_password = Column(String(128), nullable=True)
    
    # Professional Information
    specialist_type = Column(Enum(SpecialistTypeEnum), nullable=True)
    years_experience = Column(Integer, default=0, nullable=True)
    
    # Contact & Location
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    clinic_name = Column(String(200), nullable=True)
    country = Column(String(100), default="Pakistan")
    
    # Practice Information
    consultation_fee = Column(Numeric(10, 2), nullable=True)
    bio = Column(Text, nullable=True)
    languages_spoken = Column(JSON, nullable=True)
    
    # Status
    availability_status = Column(Enum(AvailabilityStatusEnum), default=AvailabilityStatusEnum.ACCEPTING_NEW_PATIENTS, nullable=False)
    approval_status = Column(Enum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING, nullable=False)
    account_status = Column(Enum(AccountStatusEnum), default=AccountStatusEnum.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_otp = Column(String(10), nullable=True)
    otp_created_at = Column(DateTime, nullable=True)
    
    # JSON Profile Meta 
    education_records = Column(JSON, nullable=True)
    experience_records = Column(JSON, nullable=True)
    specialties_in_mental_health = Column(JSON, nullable=True)
    therapy_methods = Column(JSON, nullable=True)
    documents = Column(JSON, nullable=True) # URL of document