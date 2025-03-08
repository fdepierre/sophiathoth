from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    CategoryRequest,
    CategoryResponse
)
from app.embeddings import embedding_service
from app.models.embeddings import KnowledgeBase

router = APIRouter()


@router.post("/", response_model=KnowledgeBaseResponse)
def create_knowledge_base_entry(
    entry: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    user_id: str = None  # Would come from auth middleware
):
    """
    Create a knowledge base entry
    """
    try:
        result = embedding_service.create_knowledge_base_entry(
            db=db,
            title=entry.title,
            content=entry.content,
            category=entry.category,
            tags=entry.tags,
            source=entry.source,
            confidence_score=entry.confidence_score,
            created_by=user_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating knowledge base entry: {str(e)}"
        )


@router.get("/", response_model=List[KnowledgeBaseResponse])
def get_knowledge_base_entries(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    Get knowledge base entries
    """
    query = db.query(KnowledgeBase)
    
    if category:
        query = query.filter(KnowledgeBase.category == category)
    
    entries = query.offset(skip).limit(limit).all()
    return entries


@router.get("/{entry_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific knowledge base entry
    """
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found"
        )
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a knowledge base entry
    """
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found"
        )
    
    db.delete(entry)
    db.commit()
    
    return None


@router.post("/categorize", response_model=CategoryResponse)
def categorize_text(
    request: CategoryRequest,
    db: Session = Depends(get_db)
):
    """
    Categorize text using semantic categories
    """
    try:
        result = embedding_service.categorize_text(
            db=db,
            text=request.text
        )
        
        return CategoryResponse(
            category=result["category"],
            confidence=result["confidence"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error categorizing text: {str(e)}"
        )
