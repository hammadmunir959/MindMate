from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, BaseModel
from .enums import USERTYPE, ForumCategoryEnum

class ForumQuestion(Base, BaseModel):
    """Simplified forum questions model"""
    __tablename__ = "forum_questions"

    # Author info (Polymorphic-ish association)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_type = Column(Enum(USERTYPE), nullable=False)
    
    # Metadata
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(ForumCategoryEnum), default=ForumCategoryEnum.GENERAL, nullable=False)
    
    # Privacy
    is_anonymous = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    answers = relationship("ForumAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ForumQuestion(title={self.title[:30]}, user_id={self.user_id})>"

class ForumAnswer(Base, BaseModel):
    """Simplified forum answers model"""
    __tablename__ = "forum_answers"

    question_id = Column(UUID(as_uuid=True), ForeignKey("forum_questions.id"), nullable=False, index=True)
    
    # Specialist only (Verified/Active check in service layer)
    specialist_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    
    # Relationships
    question = relationship("ForumQuestion", back_populates="answers")

    def __repr__(self):
        return f"<ForumAnswer(question_id={self.question_id}, specialist_id={self.specialist_id})>"
