from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.schemas.forum import (
    ForumQuestionCreate, ForumQuestionResponse, 
    ForumQuestionListResponse, ForumAnswerCreate, ForumAnswerResponse
)
from app.services.forum import ForumService
from app.api.v1.deps import get_current_user_payload, get_current_admin
from app.models.enums import USERTYPE, ApprovalStatusEnum
from app.models.specialist import Specialist

router = APIRouter()

# ==========================================
# PUBLIC ENDPOINTS
# ==========================================

@router.get("/questions", response_model=ForumQuestionListResponse)
def list_questions(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List all questions (Public)."""
    questions, total = ForumService.list_questions(db, category=category, page=page, page_size=page_size)
    
    # Format responses (handle anonymity)
    formatted_questions = [
        ForumService.format_question_response(db, q) for q in questions
    ]
    
    return {
        "questions": formatted_questions,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/questions/{id}", response_model=ForumQuestionResponse)
def get_question(
    id: UUID,
    db: Session = Depends(get_db)
):
    """Get question details (Public)."""
    question = ForumService.get_question(db, id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return ForumService.format_question_response(db, question)

# ==========================================
# PROTECTED ENDPOINTS (Questions)
# ==========================================

@router.post("/questions", response_model=ForumQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question_in: ForumQuestionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_payload)
):
    """Create a new question. Requires auth."""
    user_id = UUID(current_user["user_id"])
    user_type = current_user["user_type"]
    
    question = ForumService.create_question(db, user_id=user_id, user_type=user_type, data=question_in)
    return ForumService.format_question_response(db, question, requester_id=user_id)

@router.delete("/questions/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_payload)
):
    """Delete a question. Only owner or admin."""
    question = ForumService.get_question(db, id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    user_id = UUID(current_user["user_id"])
    user_type = current_user["user_type"]
    
    if user_type != USERTYPE.ADMIN.value and question.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this question")
        
    ForumService.delete_question(db, db_obj=question)
    return None

# ==========================================
# PROTECTED ENDPOINTS (Answers)
# ==========================================

@router.post("/questions/{id}/answers", response_model=ForumAnswerResponse, status_code=status.HTTP_201_CREATED)
def create_answer(
    id: UUID,
    answer_in: ForumAnswerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_payload)
):
    """Create an answer. Only Verified Specialists."""
    if current_user["user_type"] != USERTYPE.SPECIALIST.value:
        raise HTTPException(status_code=403, detail="Only specialists can answer questions")
        
    specialist_id = UUID(current_user["user_id"])
    
    # Verify the specialist is approved before allowing them to answer
    specialist = db.query(Specialist).filter(Specialist.id == specialist_id).first()
    if not specialist or specialist.approval_status != ApprovalStatusEnum.APPROVED:
        raise HTTPException(status_code=403, detail="Only approved specialists can answer questions")
    
    return ForumService.create_answer(db, specialist_id=specialist_id, question_id=id, data=answer_in)

@router.delete("/answers/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_payload)
):
    """Delete an answer. Only owner or admin."""
    answer = ForumService.get_answer(db, id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
        
    user_id = UUID(current_user["user_id"])
    user_type = current_user["user_type"]
    
    # Check if admin or the specialist who wrote it
    if user_type != USERTYPE.ADMIN.value and answer.specialist_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this answer")
        
    ForumService.delete_answer(db, db_obj=answer)
    return None
