"""
Registration Service for Specialist Management
Handles specialist registration, progress tracking, and validation
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import hashlib
import re

from app.models.specialist import (
    Specialists, 
    SpecialistsAuthInfo, 
    SpecialistsApprovalData,
    SpecialistRegistrationProgress,
    ApprovalStatusEnum,
    EmailVerificationStatusEnum,
    SpecialistTypeEnum
)
from app.schemas.auth import SpecialistRegisterRequest
from app.utils.email_utils import generate_otp, get_otp_expiry
import bcrypt

class RegistrationService:
    """Service for handling specialist registration and progress tracking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    
    async def check_existing_registration(self, email: str) -> Dict[str, Any]:
        """Check if email already exists for specialist registration"""
        existing_specialist = self.db.query(Specialists).filter(
            Specialists.email == email.lower(),
            Specialists.is_deleted == False
        ).first()
        
        if existing_specialist:
            # Check if email is verified
            auth_info = self.db.query(SpecialistsAuthInfo).filter(
                SpecialistsAuthInfo.specialist_id == existing_specialist.id
            ).first()
            
            if auth_info and auth_info.email_verification_status == EmailVerificationStatusEnum.VERIFIED:
                # Email is verified - account is registered
                    return {
                    "exists": True,
                    "message": "Email already registered with a verified account. Please login instead.",
                    "specialist_id": str(existing_specialist.id),
                    "approval_status": existing_specialist.approval_status.value if existing_specialist.approval_status else None,
                    "is_verified": True
                }
            elif auth_info and auth_info.email_verification_status == EmailVerificationStatusEnum.PENDING:
                # Email is not verified - pending verification
                return {
                "exists": True,
                    "message": "A registration with this email is pending verification. Please check your email for the OTP or request a new one.",
                "specialist_id": str(existing_specialist.id),
                    "approval_status": existing_specialist.approval_status.value if existing_specialist.approval_status else None,
                    "is_verified": False
            }
        
        return {"exists": False, "message": "Email available"}
    
    async def validate_registration_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate registration data"""
        errors = []
        
        # Validate email
        if 'email' in request and not self.email_regex.match(request['email']):
            errors.append("Invalid email format")
        
        # Validate password
        if 'password' in request and len(request['password']) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Validate phone (if provided)
        if 'phone' in request and request['phone'] and not self.phone_regex.match(request['phone']):
            errors.append("Invalid phone number format")
        
        # Validate terms acceptance
        if 'accepts_terms_and_conditions' in request and not request['accepts_terms_and_conditions']:
            errors.append("Terms and conditions must be accepted")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    async def create_specialist(self, request: Dict[str, Any]) -> Specialists:
        """Create specialist record with comprehensive data"""
        # Convert specialist_type to enum if it's a string
        specialist_type = request.get('specialist_type', None)
        if isinstance(specialist_type, str):
            # Try direct matching first (handles lowercase values like "psychiatrist")
            try:
                specialist_type = SpecialistTypeEnum(specialist_type)
            except (ValueError, AttributeError):
                # Fallback: try uppercase enum names (handles "PSYCHIATRIST")
                try:
                    specialist_type = SpecialistTypeEnum[specialist_type.upper()]
                except (KeyError, AttributeError):
                    specialist_type = None
        
        specialist = Specialists(
            id=uuid.uuid4(),
            first_name=request['first_name'],
            last_name=request['last_name'],
            email=request['email'].lower(),
            specialist_type=specialist_type,
            years_experience=request.get('years_experience', None),
            phone=request.get('phone', None),
            approval_status=ApprovalStatusEnum.PENDING,
            accepts_terms_and_conditions=request['accepts_terms_and_conditions'],
            profile_completion_percentage=0,
            mandatory_fields_completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(specialist)
        self.db.flush()
        return specialist
    
    async def create_auth_info(self, specialist_id: Any, password: str) -> SpecialistsAuthInfo:
        """Create authentication info with OTP"""
        otp = generate_otp()
        otp_expiry = get_otp_expiry()
        
        # Hash password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        auth_info = SpecialistsAuthInfo(
            specialist_id=specialist_id,
            hashed_password=hashed_password,
            otp_code=otp,
            otp_expires_at=otp_expiry,
            email_verification_status=EmailVerificationStatusEnum.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(auth_info)
        return auth_info
    
    async def create_approval_data(self, specialist_id: Any) -> SpecialistsApprovalData:
        """Create approval data record"""
        approval_data = SpecialistsApprovalData(
            specialist_id=specialist_id,
            registration_documents={},
            background_check_status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(approval_data)
        return approval_data
    
    async def create_registration_progress(self, specialist_id: Any) -> SpecialistRegistrationProgress:
        """Create registration progress tracking"""
        progress = SpecialistRegistrationProgress(
            specialist_id=specialist_id,
            step_name="registration",
            step_data={"completed": True, "timestamp": datetime.now(timezone.utc).isoformat()},
            completed_at=datetime.now(timezone.utc)
        )
        
        self.db.add(progress)
        return progress
    
    async def update_registration_progress(self, specialist_id: Any, step_name: str, step_data: Optional[Dict] = None) -> SpecialistRegistrationProgress:
        """Update registration progress for a specific step"""
        # Check if progress record already exists
        existing_progress = self.db.query(SpecialistRegistrationProgress).filter(
            SpecialistRegistrationProgress.specialist_id == specialist_id,
            SpecialistRegistrationProgress.step_name == step_name
        ).first()
        
        if existing_progress:
            # Update existing record
            existing_progress.completed_at = datetime.now(timezone.utc)
            existing_progress.step_data = step_data or {"completed": True, "timestamp": datetime.now(timezone.utc).isoformat()}
            existing_progress.updated_at = datetime.now(timezone.utc)
            return existing_progress
        else:
            # Create new record
            progress = SpecialistRegistrationProgress(
                specialist_id=specialist_id,
                step_name=step_name,
                step_data=step_data or {"completed": True, "timestamp": datetime.now(timezone.utc).isoformat()},
                completed_at=datetime.now(timezone.utc)
            )
            self.db.add(progress)
            return progress
    
    async def get_registration_progress(self, specialist_id: str) -> Dict[str, Any]:
        """Get registration progress for specialist"""
        progress_records = self.db.query(SpecialistRegistrationProgress).filter(
            SpecialistRegistrationProgress.specialist_id == specialist_id
        ).all()
        
        completed_steps = [record.step_name for record in progress_records if record.completed_at]
        total_steps = ["registration", "email_verification", "profile_completion", "document_upload", "admin_approval"]
        
        progress_percentage = (len(completed_steps) / len(total_steps)) * 100
        
        # Get current step
        current_step = None
        if len(completed_steps) < len(total_steps):
            current_step = total_steps[len(completed_steps)]
        
        return {
            "specialist_id": specialist_id,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "progress_percentage": progress_percentage,
            "current_step": current_step,
            "is_complete": len(completed_steps) == len(total_steps)
        }
    
    async def get_specialist_by_id(self, specialist_id: str) -> Optional[Specialists]:
        """Get specialist by ID"""
        return self.db.query(Specialists).filter(Specialists.id == specialist_id).first()
    
    async def get_specialist_by_email(self, email: str) -> Optional[Specialists]:
        """Get specialist by email"""
        return self.db.query(Specialists).filter(Specialists.email == email.lower()).first()
    
    async def update_specialist_status(self, specialist_id: str, status_updates: Dict[str, Any]) -> Specialists:
        """Update specialist status and related fields"""
        specialist = await self.get_specialist_by_id(specialist_id)
        if not specialist:
            raise ValueError(f"Specialist not found: {specialist_id}")
        
        # Update fields
        for field, value in status_updates.items():
            if hasattr(specialist, field):
                setattr(specialist, field, value)
        
        specialist.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(specialist)
        return specialist
    
    async def get_specialist_registration_summary(self, specialist_id: str) -> Dict[str, Any]:
        """Get comprehensive registration summary for specialist"""
        specialist = await self.get_specialist_by_id(specialist_id)
        if not specialist:
            raise ValueError(f"Specialist not found: {specialist_id}")
        
        progress = await self.get_registration_progress(specialist_id)
        
        # Get approval data
        approval_data = self.db.query(SpecialistsApprovalData).filter(
            SpecialistsApprovalData.specialist_id == specialist_id
        ).first()
        
        return {
            "specialist": {
                "id": str(specialist.id),
                "email": specialist.email,
                "first_name": specialist.first_name,
                "last_name": specialist.last_name,
                "approval_status": specialist.approval_status.value if specialist.approval_status else None,
                "profile_completion_percentage": specialist.profile_completion_percentage,
                "mandatory_fields_completed": specialist.mandatory_fields_completed,
                "created_at": specialist.created_at.isoformat() if specialist.created_at else None
            },
            "progress": progress,
            "approval_data": {
                "approval_timeline": approval_data.approval_timeline if approval_data else None,
                "document_verification_status": approval_data.document_verification_status if approval_data else None,
                "background_check_status": approval_data.background_check_status if approval_data else None,
                "compliance_check_status": approval_data.compliance_check_status if approval_data else None
            } if approval_data else None
        }
