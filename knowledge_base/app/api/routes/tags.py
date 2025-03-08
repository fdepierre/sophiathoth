from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.knowledge import Tag
from app.schemas import (
    TagCreate,
    TagResponse
)

router = APIRouter()


@router.post("/", response_model=TagResponse)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tag
    """
    # Check if tag already exists
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag.name}' already exists"
        )
    
    # Create new tag
    db_tag = Tag(
        name=tag.name,
        description=tag.description
    )
    
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    
    return db_tag


@router.get("/", response_model=List[TagResponse])
def get_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all tags
    """
    tags = db.query(Tag).offset(skip).limit(limit).all()
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tag
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: str,
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """
    Update a tag
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if name already exists for a different tag
    if tag.name != db_tag.name:
        existing = db.query(Tag).filter(Tag.name == tag.name).first()
        if existing and existing.id != tag_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag.name}' already exists"
            )
    
    # Update tag
    db_tag.name = tag.name
    db_tag.description = tag.description
    
    db.commit()
    db.refresh(db_tag)
    
    return db_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a tag
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    db.delete(db_tag)
    db.commit()
    
    return None
