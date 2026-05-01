from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
import uuid
from datetime import datetime
from app.models.enums import USERTYPE, ForumCategoryEnum

# ==========================================
# ANSWER SCHEMAS
# ==========================================

class ForumAnswerBase(BaseModel):
    content: str = Field(..., min_length=10)

class ForumAnswerCreate(ForumAnswerBase):
    pass

class ForumAnswerResponse(ForumAnswerBase):
    id: uuid.UUID
    question_id: uuid.UUID
    specialist_id: uuid.UUID
    created_at: datetime
    specialist_name: Optional[str] = None # Filled by service layer

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# QUESTION SCHEMAS
# ==========================================

class ForumQuestionBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    content: str = Field(..., min_length=10)
    category: ForumCategoryEnum = Field(default=ForumCategoryEnum.GENERAL)
    is_anonymous: bool = Field(default=False)

class ForumQuestionCreate(ForumQuestionBase):
    pass

class ForumQuestionResponse(ForumQuestionBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None # Shared if not anonymous or if requester is owner
    user_type: Optional[USERTYPE] = None
    author_name: Optional[str] = None # "Anonymous" if anonymous
    created_at: datetime
    answers: List[ForumAnswerResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ForumQuestionListResponse(BaseModel):
    questions: List[ForumQuestionResponse]
    total: int
    page: int
    page_size: int
