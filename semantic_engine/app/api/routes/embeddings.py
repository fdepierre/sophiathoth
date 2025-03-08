from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    QuestionEmbeddingCreate,
    ResponseEmbeddingCreate,
    QuestionEmbeddingResponse,
    ResponseEmbeddingResponse,
    SimilarityRequest,
    SimilarityResponse
)
from app.embeddings import embedding_service

router = APIRouter()


@router.post("/questions", response_model=QuestionEmbeddingResponse)
def create_question_embedding(
    embedding: QuestionEmbeddingCreate,
    db: Session = Depends(get_db)
):
    """
    Create embedding for a question
    """
    try:
        result = embedding_service.create_question_embedding(
            db=db,
            question_id=embedding.question_id,
            text=embedding.text
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating question embedding: {str(e)}"
        )


@router.post("/responses", response_model=ResponseEmbeddingResponse)
def create_response_embedding(
    embedding: ResponseEmbeddingCreate,
    db: Session = Depends(get_db)
):
    """
    Create embedding for a response
    """
    try:
        result = embedding_service.create_response_embedding(
            db=db,
            response_id=embedding.response_id,
            text=embedding.text
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating response embedding: {str(e)}"
        )


@router.post("/similar-questions", response_model=SimilarityResponse)
def find_similar_questions(
    request: SimilarityRequest,
    db: Session = Depends(get_db)
):
    """
    Find similar questions using vector similarity
    """
    try:
        # Generate embedding for query
        query_embedding = embedding_service.generate_embedding(request.text)
        
        # Find similar questions
        similar_questions = embedding_service.find_similar_questions(
            db=db,
            text=request.text,
            limit=request.limit,
            threshold=request.threshold
        )
        
        return SimilarityResponse(
            results=similar_questions,
            query_embedding=query_embedding
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar questions: {str(e)}"
        )


@router.post("/similar-knowledge", response_model=SimilarityResponse)
def find_similar_knowledge(
    request: SimilarityRequest,
    db: Session = Depends(get_db)
):
    """
    Find similar knowledge base entries using vector similarity
    """
    try:
        # Generate embedding for query
        query_embedding = embedding_service.generate_embedding(request.text)
        
        # Find similar knowledge base entries
        similar_knowledge = embedding_service.find_similar_knowledge(
            db=db,
            text=request.text,
            limit=request.limit,
            threshold=request.threshold
        )
        
        return SimilarityResponse(
            results=similar_knowledge,
            query_embedding=query_embedding
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar knowledge: {str(e)}"
        )
