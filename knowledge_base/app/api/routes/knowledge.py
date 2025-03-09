from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.models.knowledge import KnowledgeEntry, KnowledgeCategory, Tag, KnowledgeAttachment, KnowledgeRevision
from app.schemas import (
    KnowledgeEntryCreate,
    KnowledgeEntryUpdate,
    KnowledgeEntryResponse,
    KnowledgeAttachmentResponse,
    KnowledgeRevisionResponse,
    SearchRequest,
    SearchResponse
)
from app.storage import minio_client
from app.semantic import semantic_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=KnowledgeEntryResponse)
async def create_knowledge_entry(
    entry: KnowledgeEntryCreate,
    db: Session = Depends(get_db),
    user_id: str = None  # Would come from auth middleware
):
    """
    Create a new knowledge entry
    """
    # Check if category exists if specified
    if entry.category_id:
        category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == entry.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID '{entry.category_id}' not found"
            )
    
    # Create new knowledge entry
    db_entry = KnowledgeEntry(
        title=entry.title,
        content=entry.content,
        summary=entry.summary,
        source_type=entry.source_type,
        source_id=entry.source_id,
        category_id=entry.category_id,
        entry_metadata=entry.entry_metadata,
        created_by=user_id
    )
    
    # Add entry to session first
    db.add(db_entry)
    db.flush()
    
    # Process tags after entry is in session
    if entry.tags:
        for tag_name in entry.tags:
            # Check if tag exists by name or ID
            tag = db.query(Tag).filter(
                (Tag.name == tag_name) | (Tag.id == tag_name)
            ).first()
            
            # Create tag if it doesn't exist
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
            
            # Make sure both objects are in the same session
            db.refresh(tag)
            db.refresh(db_entry)
            
            # Use SQLAlchemy's relationship management
            if tag not in db_entry.tags:
                db_entry.tags.append(tag)
                db.flush()  # Flush after each tag to ensure it's properly associated
    
    # Try to categorize if no category provided
    if not entry.category_id:
        try:
            category_result = await semantic_client.categorize_text(f"{entry.title} {entry.content}")
            if category_result["category"] != "uncategorized" and category_result["confidence"] > 0.7:
                # Find or create category
                category = db.query(KnowledgeCategory).filter(
                    KnowledgeCategory.name == category_result["category"]
                ).first()
                
                if not category:
                    category = KnowledgeCategory(
                        name=category_result["category"],
                        description=f"Auto-generated category for '{category_result['category']}'"
                    )
                    db.add(category)
                    db.flush()
                
                db_entry.category_id = category.id
        except Exception as e:
            logger.error(f"Error auto-categorizing knowledge entry: {e}")
    
    # Entry is already added to session above
    # Now create initial revision after we have a valid ID
    revision = KnowledgeRevision(
        knowledge_id=db_entry.id,  # This ID is now valid since we've flushed the session
        version=1,
        title=entry.title,
        content=entry.content,
        summary=entry.summary,
        entry_metadata=entry.entry_metadata,
        created_by=user_id
    )
    
    db.add(revision)
    
    db.commit()
    db.refresh(db_entry)
    
    return db_entry


@router.get("/", response_model=List[KnowledgeEntryResponse])
def get_knowledge_entries(
    category_id: Optional[str] = None,
    tag: Optional[str] = None,
    source_type: Optional[str] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get knowledge entries with optional filtering
    """
    query = db.query(KnowledgeEntry)
    
    if category_id:
        query = query.filter(KnowledgeEntry.category_id == category_id)
    
    if source_type:
        query = query.filter(KnowledgeEntry.source_type == source_type)
    
    if is_active is not None:
        query = query.filter(KnowledgeEntry.is_active == is_active)
    
    if tag:
        query = query.join(KnowledgeEntry.tags).filter(
            (Tag.name == tag) | (Tag.id == tag)
        )
    
    entries = query.offset(skip).limit(limit).all()
    return entries


@router.get("/{entry_id}", response_model=KnowledgeEntryResponse)
def get_knowledge_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific knowledge entry
    """
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    return entry


@router.put("/{entry_id}", response_model=KnowledgeEntryResponse)
async def update_knowledge_entry(
    entry_id: str,
    entry_update: KnowledgeEntryUpdate,
    db: Session = Depends(get_db),
    user_id: str = None  # Would come from auth middleware
):
    """
    Update a knowledge entry
    """
    db_entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    # Check if category exists if specified
    if entry_update.category_id is not None:
        if entry_update.category_id:  # Not None and not empty string
            category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == entry_update.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID '{entry_update.category_id}' not found"
                )
        db_entry.category_id = entry_update.category_id
    
    # Update fields if provided
    if entry_update.title is not None:
        db_entry.title = entry_update.title
    
    if entry_update.content is not None:
        db_entry.content = entry_update.content
    
    if entry_update.summary is not None:
        db_entry.summary = entry_update.summary
    
    if entry_update.is_active is not None:
        db_entry.is_active = entry_update.is_active
    
    if entry_update.entry_metadata is not None:
        db_entry.entry_metadata = entry_update.entry_metadata
    
    # Process tags if provided
    if entry_update.tags is not None:
        # Clear existing tags
        db_entry.tags = []
        
        # Add new tags
        for tag_name in entry_update.tags:
            # Check if tag exists by name or ID
            tag = db.query(Tag).filter(
                (Tag.name == tag_name) | (Tag.id == tag_name)
            ).first()
            
            # Create tag if it doesn't exist
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
            
            db_entry.tags.append(tag)
    
    # Increment version and create new revision
    db_entry.version += 1
    
    revision = KnowledgeRevision(
        knowledge_id=entry_id,
        version=db_entry.version,
        title=db_entry.title,
        content=db_entry.content,
        summary=db_entry.summary,
        entry_metadata=db_entry.entry_metadata,
        created_by=user_id
    )
    
    db.add(revision)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a knowledge entry
    """
    db_entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    # Delete attachments from storage
    for attachment in db_entry.attachments:
        minio_client.delete_file(attachment.storage_path)
    
    db.delete(db_entry)
    db.commit()
    
    return None


@router.post("/{entry_id}/attachments", response_model=KnowledgeAttachmentResponse)
async def upload_attachment(
    entry_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an attachment for a knowledge entry
    """
    # Check if entry exists
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to MinIO
        storage_path = minio_client.upload_file(
            file_data=file_content,
            content_type=file.content_type,
            filename=f"knowledge_{entry_id}_{file.filename}"
        )
        
        # Create attachment record
        attachment = KnowledgeAttachment(
            knowledge_id=entry_id,
            filename=storage_path,
            original_filename=file.filename,
            content_type=file.content_type,
            size_bytes=len(file_content),
            storage_path=storage_path
        )
        
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        
        return attachment
    
    except Exception as e:
        logger.error(f"Error uploading attachment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading attachment: {str(e)}"
        )


@router.get("/{entry_id}/attachments", response_model=List[KnowledgeAttachmentResponse])
def get_attachments(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all attachments for a knowledge entry
    """
    # Check if entry exists
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    return entry.attachments


@router.get("/{entry_id}/attachments/{attachment_id}")
async def download_attachment(
    entry_id: str,
    attachment_id: str,
    db: Session = Depends(get_db)
):
    """
    Download an attachment for a knowledge entry
    """
    # Check if entry exists
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    # Check if attachment exists and belongs to the entry
    attachment = db.query(KnowledgeAttachment).filter(
        KnowledgeAttachment.id == attachment_id,
        KnowledgeAttachment.knowledge_id == entry_id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    try:
        # Download file from MinIO
        file_data = minio_client.download_file(attachment.storage_path)
        
        # Create a response with the file data
        from fastapi.responses import Response
        return Response(
            content=file_data,
            media_type=attachment.content_type,
            headers={
                "Content-Disposition": f"attachment; filename={attachment.original_filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"Error downloading attachment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading attachment: {str(e)}"
        )


@router.get("/{entry_id}/revisions", response_model=List[KnowledgeRevisionResponse])
def get_revisions(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all revisions for a knowledge entry
    """
    # Check if entry exists
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    return entry.revisions


@router.get("/search", response_model=SearchResponse)
async def search_knowledge_get(
    query: str,
    limit: int = 10,
    offset: int = 0,
    category_id: Optional[str] = None,
    source_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search knowledge entries using semantic search (GET method)
    """
    # Create filters dictionary
    filters = {}
    if category_id:
        filters["category_id"] = category_id
    if source_type:
        filters["source_type"] = source_type
    if is_active is not None:
        filters["is_active"] = is_active
    if tag:
        filters["tag"] = tag
        
    # Create search request
    search_request = SearchRequest(
        query=query,
        limit=limit,
        offset=offset,
        filters=filters
    )
    
    # Call the POST search method
    return await search_knowledge_post(search_request, db)

@router.post("/search", response_model=SearchResponse)
async def search_knowledge_post(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search knowledge entries using semantic search
    """
    try:
        # Try to get similar knowledge from semantic engine
        similar_knowledge = await semantic_client.find_similar_knowledge(
            text=search_request.query,
            limit=search_request.limit,
            threshold=0.6
        )
        
        # Extract IDs
        knowledge_ids = [item["id"] for item in similar_knowledge]
        
        # If semantic search returned results, use them
        if knowledge_ids:
            # Query database for full entries
            query = db.query(KnowledgeEntry).filter(KnowledgeEntry.id.in_(knowledge_ids))
        else:
            # Fallback to basic text search if semantic search is not available or returned no results
            logger.info(f"No semantic search results for query: {search_request.query}, falling back to basic search")
            query = db.query(KnowledgeEntry).filter(
                KnowledgeEntry.title.ilike(f"%{search_request.query}%") | 
                KnowledgeEntry.content.ilike(f"%{search_request.query}%") |
                KnowledgeEntry.summary.ilike(f"%{search_request.query}%")
            )
        
        # Apply additional filters if provided
        if search_request.filters:
            if "category_id" in search_request.filters:
                query = query.filter(KnowledgeEntry.category_id == search_request.filters["category_id"])
            
            if "source_type" in search_request.filters:
                query = query.filter(KnowledgeEntry.source_type == search_request.filters["source_type"])
            
            if "is_active" in search_request.filters:
                query = query.filter(KnowledgeEntry.is_active == search_request.filters["is_active"])
            
            if "tag" in search_request.filters:
                query = query.join(KnowledgeEntry.tags).filter(
                    (Tag.name == search_request.filters["tag"]) | (Tag.id == search_request.filters["tag"])
                )
        
        # Get total count
        total = query.count()
        
        # Check if any entries were found
        if total == 0:
            return SearchResponse(
                results=[],
                total=0,
                query=search_request.query
            )
        
        # Apply pagination
        entries = query.offset(search_request.offset).limit(search_request.limit).all()
        
        # Sort entries based on similarity score if semantic search was used
        if knowledge_ids:
            similarity_map = {item["id"]: item["similarity"] for item in similar_knowledge}
            sorted_entries = sorted(
                entries,
                key=lambda entry: similarity_map.get(entry.id, 0),
                reverse=True
            )
        else:
            # For basic search, just use the entries as they are
            sorted_entries = entries
        
        return SearchResponse(
            results=sorted_entries,
            total=total,
            query=search_request.query
        )
    
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching knowledge: {str(e)}"
        )
