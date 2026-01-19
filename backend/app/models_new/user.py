"""
User & Authentication Models
=============================
Unified authentication with polymorphic user profiles.
"""

from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime, ForeignKey, Enum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models_new.base import BaseModel, UserType


class User(BaseModel):
    """
    Unified user authentication table.
    Links to Patient, Specialist, or Admin profile.
    """
    __tablename__ = "users"
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    
    # Profile reference (polymorphic)
    profile_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Status
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    # Security
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Profile Relationships (One-to-One)
    patient = relationship(
        "Patient",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )
    specialist = relationship(
        "Specialist",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_type', 'user_type'),
    )
    
    def __repr__(self):
        return f"<User {self.email} ({self.user_type.value})>"


class PasswordResetToken(BaseModel):
    """Password reset tokens for secure password recovery"""
    __tablename__ = "password_reset_tokens"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")
    
    __table_args__ = (
        Index('idx_reset_tokens_user', 'user_id'),
        Index('idx_reset_tokens_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<PasswordResetToken for user {self.user_id}>"


__all__ = ["User", "PasswordResetToken"]
