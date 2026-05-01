from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import List, Optional, Tuple
from fastapi import HTTPException, status

from app.models.forum import ForumQuestion, ForumAnswer
from app.models.specialist import Specialist
from app.models.patient import Patient
from app.models.enums import USERTYPE, AccountStatusEnum, ForumCategoryEnum
from app.schemas.forum import (
    ForumQuestionCreate, ForumQuestionResponse, 
    ForumAnswerCreate, ForumAnswerResponse
)

class ForumService:
    """Service class holding business logic for the Forum."""

    # ==========================================
    # QUESTION LOGIC
    # ==========================================

    @staticmethod
    def create_question(db: Session, user_id: UUID, user_type: USERTYPE, data: ForumQuestionCreate) -> ForumQuestion:
        """Creates a new forum question."""
        db_obj = ForumQuestion(
            user_id=user_id,
            user_type=user_type,
            title=data.title,
            content=data.content,
            category=data.category,
            is_anonymous=data.is_anonymous
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def list_questions(
        db: Session, 
        category: Optional[ForumCategoryEnum] = None,
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[ForumQuestion], int]:
        """Lists questions with optional category filtering and pagination."""
        query = db.query(ForumQuestion).filter(ForumQuestion.is_deleted == False)
        
        if category:
            query = query.filter(ForumQuestion.category == category)
            
        total = query.count()
        questions = query.order_by(ForumQuestion.created_at.desc())\
                        .offset((page - 1) * page_size)\
                        .limit(page_size)\
                        .all()
        
        return questions, total

    @staticmethod
    def get_question(db: Session, question_id: UUID) -> Optional[ForumQuestion]:
        """Retrieves a single question by ID."""
        return db.query(ForumQuestion).filter(
            ForumQuestion.id == question_id, 
            ForumQuestion.is_deleted == False
        ).first()

    @staticmethod
    def delete_question(db: Session, db_obj: ForumQuestion) -> ForumQuestion:
        """Soft deletes a question."""
        db_obj.is_deleted = True
        db.commit()
        return db_obj

    # ==========================================
    # ANSWER LOGIC
    # ==========================================

    @staticmethod
    def create_answer(db: Session, specialist_id: UUID, question_id: UUID, data: ForumAnswerCreate) -> ForumAnswer:
        """Creates an answer. Validates specialist status first."""
        # 1. Verify specialist is Active and Verified
        specialist = db.query(Specialist).filter(
            Specialist.id == specialist_id,
            Specialist.is_deleted == False
        ).first()

        if not specialist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")

        if not specialist.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Only verified specialists can answer questions"
            )
        
        if specialist.account_status != AccountStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Your account must be active to answer questions"
            )

        # 2. Check if question exists
        question = db.query(ForumQuestion).filter(
            ForumQuestion.id == question_id,
            ForumQuestion.is_deleted == False
        ).first()

        if not question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

        # 3. Create answer
        db_obj = ForumAnswer(
            question_id=question_id,
            specialist_id=specialist_id,
            content=data.content
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_answers(db: Session, question_id: UUID) -> List[ForumAnswer]:
        """Gets all answers for a question."""
        return db.query(ForumAnswer).filter(
            ForumAnswer.question_id == question_id,
            ForumAnswer.is_deleted == False
        ).order_by(ForumAnswer.created_at.asc()).all()

    @staticmethod
    def get_answer(db: Session, answer_id: UUID) -> Optional[ForumAnswer]:
        """Retrieves a single answer by ID."""
        return db.query(ForumAnswer).filter(
            ForumAnswer.id == answer_id,
            ForumAnswer.is_deleted == False
        ).first()

    @staticmethod
    def delete_answer(db: Session, db_obj: ForumAnswer) -> ForumAnswer:
        """Soft deletes an answer."""
        db_obj.is_deleted = True
        db.commit()
        return db_obj

    # ==========================================
    # DATA FORMATTING (Helper for Anonymity)
    # ==========================================

    @staticmethod
    def format_question_response(db: Session, question: ForumQuestion, requester_id: Optional[UUID] = None) -> ForumQuestionResponse:
        """Formats the question model into a response schema, handling anonymity."""
        response = ForumQuestionResponse.model_validate(question)
        
        # Determine if we should show author info
        is_owner = requester_id == question.user_id
        show_author = not question.is_anonymous or is_owner
        
        if show_author:
            # Fetch author name
            if question.user_type == USERTYPE.PATIENT:
                author = db.query(Patient).filter(Patient.id == question.user_id).first()
                if author:
                    response.author_name = f"{author.first_name} {author.last_name}"
            elif question.user_type == USERTYPE.SPECIALIST:
                author = db.query(Specialist).filter(Specialist.id == question.user_id).first()
                if author:
                    response.author_name = f"Dr. {author.first_name} {author.last_name}"
        else:
            # Mask author info
            response.user_id = None
            response.user_type = None
            response.author_name = "Anonymous Patient" if question.user_type == USERTYPE.PATIENT else "Anonymous Specialist"

        # Format answers
        answers = []
        for ans in question.answers:
            if not ans.is_deleted:
                ans_resp = ForumAnswerResponse.model_validate(ans)
                # Fetch specialist name
                spec = db.query(Specialist).filter(Specialist.id == ans.specialist_id).first()
                if spec:
                    ans_resp.specialist_name = f"Dr. {spec.first_name} {spec.last_name}"
                answers.append(ans_resp)
        
        response.answers = answers
        return response
