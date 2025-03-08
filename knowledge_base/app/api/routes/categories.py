from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.knowledge import KnowledgeCategory
from app.schemas import (
    KnowledgeCategoryCreate,
    KnowledgeCategoryResponse
)
from app.semantic import semantic_client

router = APIRouter()


@router.post("/", response_model=KnowledgeCategoryResponse)
def create_category(
    category: KnowledgeCategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge category
    """
    # Check if category already exists
    existing = db.query(KnowledgeCategory).filter(KnowledgeCategory.name == category.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.name}' already exists"
        )
    
    # Check if parent exists if specified
    if category.parent_id:
        parent = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with ID '{category.parent_id}' not found"
            )
    
    # Create new category
    db_category = KnowledgeCategory(
        name=category.name,
        description=category.description,
        parent_id=category.parent_id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.get("/", response_model=List[KnowledgeCategoryResponse])
def get_categories(
    parent_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all knowledge categories, optionally filtered by parent
    """
    query = db.query(KnowledgeCategory)
    
    if parent_id:
        query = query.filter(KnowledgeCategory.parent_id == parent_id)
    
    categories = query.offset(skip).limit(limit).all()
    return categories


@router.get("/{category_id}", response_model=KnowledgeCategoryResponse)
def get_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific knowledge category
    """
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.put("/{category_id}", response_model=KnowledgeCategoryResponse)
def update_category(
    category_id: str,
    category: KnowledgeCategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Update a knowledge category
    """
    db_category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if name already exists for a different category
    if category.name != db_category.name:
        existing = db.query(KnowledgeCategory).filter(KnowledgeCategory.name == category.name).first()
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category.name}' already exists"
            )
    
    # Check if parent exists if specified
    if category.parent_id and category.parent_id != db_category.parent_id:
        # Prevent circular references
        if category.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent"
            )
        
        parent = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with ID '{category.parent_id}' not found"
            )
    
    # Update category
    db_category.name = category.name
    db_category.description = category.description
    db_category.parent_id = category.parent_id
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a knowledge category
    """
    db_category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if category has children
    children = db.query(KnowledgeCategory).filter(KnowledgeCategory.parent_id == category_id).all()
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with child categories"
        )
    
    # Check if category has entries
    if db_category.entries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with knowledge entries"
        )
    
    db.delete(db_category)
    db.commit()
    
    return None
