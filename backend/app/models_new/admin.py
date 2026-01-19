"""
Admin Model
===========
Administrative user profile.
"""

from sqlalchemy import (
    Column, String, Boolean, ForeignKey, Enum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models_new.base import BaseModel, AdminRole


class Admin(BaseModel):
    """
    Admin user profile for platform management.
    """
    __tablename__ = "admins"
    
    # Link to unified users table
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    
    # Profile
    full_name = Column(String(200), nullable=False)
    role = Column(Enum(AdminRole), default=AdminRole.ADMIN)
    
    # Permissions (JSONB for flexibility)
    permissions = Column(JSONB, default={})
    """
    Structure:
    {
        "manage_patients": true,
        "manage_specialists": true,
        "approve_specialists": true,
        "view_reports": true,
        "manage_admins": false
    }
    """
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_admins_user', 'user_id'),
        Index('idx_admins_role', 'role'),
    )
    
    def __repr__(self):
        return f"<Admin {self.full_name} ({self.role.value})>"


__all__ = ["Admin"]
