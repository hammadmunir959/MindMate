"""
User Repository
===============
Data access for Users.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.db.repositories_new.base import BaseRepository
from app.models_new.user import User


class UserRepository(BaseRepository[User, dict, dict]):
    """
    Repository for User operations.
    """
    
    def GetByEmail(self, db: Session, email: str) -> Optional[User]:
        """Get user by email address"""
        return db.query(User).filter(User.email == email).first()
    
    def GetByProfileId(self, db: Session, profile_id: str) -> Optional[User]:
        """Get user by linked profile ID"""
        return db.query(User).filter(User.profile_id == profile_id).first()


user_repo = UserRepository(User)
