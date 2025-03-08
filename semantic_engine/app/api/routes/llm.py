from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.schemas import (
    GenerateResponseRequest,
    GenerateResponseResponse
)
from app.llm import llm_service
from app.embeddings import embedding_service

router = APIRouter()


@router.post("/generate-response", response_model=GenerateResponseResponse)
async def generate_response(
    request: GenerateResponseRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a response to a question using LLM
    """
    try:
        # If context is not provided, find similar knowledge
        if not request.context:
            similar_knowledge = embedding_service.find_similar_knowledge(
                db=db,
                text=request.question,
                limit=5,
                threshold=0.6
            )
            context = similar_knowledge
        else:
            context = request.context
        
        # Generate response
        result = await llm_service.generate_response(
            question=request.question,
            context=context,
            max_tokens=request.max_tokens
        )
        
        return GenerateResponseResponse(
            response=result["response"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


@router.post("/analyze-sentiment")
async def analyze_sentiment(
    text: str
):
    """
    Analyze sentiment of text
    """
    try:
        result = await llm_service.analyze_sentiment(text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing sentiment: {str(e)}"
        )
