from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import TenderQuestion, TenderResponse
from app.schemas import (
    TenderQuestionResponse,
    TenderQuestionCreate,
    TenderResponseResponse,
    TenderResponseCreate,
    TenderResponseUpdate
)

router = APIRouter()


@router.get("/", response_model=List[TenderQuestionResponse])
def get_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all tender questions
    """
    questions = db.query(TenderQuestion).offset(skip).limit(limit).all()
    return questions


@router.get("/{question_id}", response_model=TenderQuestionResponse)
def get_question(
    question_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tender question
    """
    question = db.query(TenderQuestion).filter(TenderQuestion.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question


@router.post("/{question_id}/responses", response_model=TenderResponseResponse)
def create_response(
    question_id: str,
    response: TenderResponseCreate,
    db: Session = Depends(get_db),
    user_id: str = None  # Would come from auth middleware
):
    """
    Create a response for a specific tender question
    """
    question = db.query(TenderQuestion).filter(TenderQuestion.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    db_response = TenderResponse(
        question_id=question_id,
        text=response.text,
        source_reference=response.source_reference,
        confidence_score=response.confidence_score,
        created_by=user_id
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    
    return db_response


@router.get("/{question_id}/responses", response_model=List[TenderResponseResponse])
def get_question_responses(
    question_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all responses for a specific tender question
    """
    question = db.query(TenderQuestion).filter(TenderQuestion.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question.responses


@router.put("/{question_id}/responses/{response_id}", response_model=TenderResponseResponse)
def update_response(
    question_id: str,
    response_id: str,
    response_update: TenderResponseUpdate,
    db: Session = Depends(get_db),
    user_id: str = None  # Would come from auth middleware
):
    """
    Update a specific response
    """
    db_response = db.query(TenderResponse).filter(
        TenderResponse.id == response_id,
        TenderResponse.question_id == question_id
    ).first()
    
    if not db_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    # Update fields
    if response_update.text is not None:
        db_response.text = response_update.text
    
    if response_update.is_approved is not None:
        db_response.is_approved = response_update.is_approved
        if response_update.is_approved:
            import datetime
            db_response.approved_by = user_id
            db_response.approved_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(db_response)
    
    return db_response
