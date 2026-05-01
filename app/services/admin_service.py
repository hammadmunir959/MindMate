from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status

from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminUpdate
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.enums import AdminRoleEnum

class AdminService:
    @staticmethod
    def get_admin(db: Session, admin_id: UUID) -> Admin:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return admin

    @staticmethod
    def get_admin_by_email(db: Session, email: str) -> Admin:
        return db.query(Admin).filter(Admin.email == email).first()

    @staticmethod
    def create_admin(db: Session, admin_in: AdminCreate) -> Admin:
        if AdminService.get_admin_by_email(db, admin_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin with this email already exists"
            )

        admin_data = admin_in.model_dump(exclude={"password"})
        hashed_password = get_password_hash(admin_in.password)
        
        admin = Admin(**admin_data, hashed_password=hashed_password)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def update_admin(db: Session, admin_id: UUID, admin_in: AdminUpdate) -> Admin:
        admin = AdminService.get_admin(db, admin_id)
        
        update_data = admin_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(admin, field, value)
            
        db.commit()
        db.refresh(admin)
        return admin
        
    @staticmethod
    def list_admins(db: Session, skip: int = 0, limit: int = 100) -> list[Admin]:
        return db.query(Admin).filter(Admin.is_deleted == False).offset(skip).limit(limit).all()

    @staticmethod
    def setup_superadmin(db: Session) -> Admin:
        # Check if superadmin already exists
        existing_super = db.query(Admin).filter(Admin.role == AdminRoleEnum.SUPER_ADMIN).first()
        if existing_super:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SuperAdmin setup has already been completed."
            )
            
        # Create SuperAdmin using env variables
        if not settings.SUPER_ADMIN_EMAIL or not settings.SUPER_ADMIN_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SuperAdmin credentials not configured in environment."
            )
            
        hashed_password = get_password_hash(settings.SUPER_ADMIN_PASSWORD)
        
        superadmin = Admin(
            first_name=settings.SUPER_ADMIN_FIRST_NAME or "Super",
            last_name=settings.SUPER_ADMIN_LAST_NAME or "Admin",
            email=settings.SUPER_ADMIN_EMAIL,
            role=AdminRoleEnum.SUPER_ADMIN,
            hashed_password=hashed_password
        )
        
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        return superadmin
