from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.models.specialist import Specialist
from app.schemas.specialist import SpecialistCreate, SpecialistUpdate
from app.core.security import get_password_hash, generate_otp
from app.services.email import email_service
from datetime import datetime, timezone

class SpecialistService:
    """Service class holding business logic for Specialists."""

    @staticmethod
    def create(db: Session, data: SpecialistCreate) -> Specialist:
        # Generate verification OTP
        otp = generate_otp()
        
        db_obj = Specialist(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            cnic_number=data.cnic_number,
            gender=data.gender,
            specialist_type=data.specialist_type,
            years_experience=data.years_experience,
            city=data.city,
            country=data.country,
            address=data.address,
            clinic_name=data.clinic_name,
            consultation_fee=data.consultation_fee,
            bio=data.bio,
            languages_spoken=data.languages_spoken,
            hashed_password=get_password_hash(data.password),
            verification_otp=otp,
            otp_created_at=datetime.now(timezone.utc)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Send verification email
        email_service.send_verification_otp(
            email=db_obj.email,
            name=f"{db_obj.first_name} {db_obj.last_name}",
            otp=otp
        )

        return db_obj

    @staticmethod
    def get(db: Session, id: UUID) -> Optional[Specialist]:
        """Retrieves a single specialist by ID."""
        return db.query(Specialist).filter(Specialist.id == id, Specialist.is_deleted == False).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Specialist]:
        """Retrieves a specialist by email."""
        return db.query(Specialist).filter(Specialist.email == email, Specialist.is_deleted == False).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> List[Specialist]:
        """
        Retrieves a paginated list of specialists for public browsing.
        Only returns specialists who are verified, approved, and active.
        """
        from app.models.enums import ApprovalStatusEnum, AccountStatusEnum
        return (
            db.query(Specialist)
            .filter(
                Specialist.is_deleted == False,
                Specialist.is_verified == True,
                Specialist.approval_status == ApprovalStatusEnum.APPROVED,
                Specialist.account_status == AccountStatusEnum.ACTIVE
            )
            .offset(skip).limit(limit).all()
        )

    @staticmethod
    def update(db: Session, db_obj: Specialist, update_data: SpecialistUpdate) -> Specialist:
        """Updates an existing specialist using the update schema."""
        # Only update fields that were actually provided (not None)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(db_obj, field, value)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Specialist) -> Specialist:
        """Performs soft delete on specialist."""
        db_obj.is_deleted = True
        db.commit()
        return db_obj
