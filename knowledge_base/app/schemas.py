from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class TagBase(BaseModel):
    """Base schema for tags"""
    name: str
    description: Optional[str] = None


class TagCreate(TagBase):
    """Schema for creating a tag"""
    pass


class TagResponse(TagBase):
    """Schema for tag response"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeCategoryBase(BaseModel):
    """Base schema for knowledge categories"""
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None


class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    """Schema for creating a knowledge category"""
    pass


class KnowledgeCategoryResponse(KnowledgeCategoryBase):
    """Schema for knowledge category response"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeEntryBase(BaseModel):
    """Base schema for knowledge entries"""
    title: str
    content: str
    summary: Optional[str] = None
    source_type: str
    source_id: Optional[str] = None
    entry_metadata: Optional[Dict[str, Any]] = None


class KnowledgeEntryCreate(KnowledgeEntryBase):
    """Schema for creating a knowledge entry"""
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None  # List of tag names or IDs


class KnowledgeEntryUpdate(BaseModel):
    """Schema for updating a knowledge entry"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = None
    entry_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None  # List of tag names or IDs


class KnowledgeEntryResponse(KnowledgeEntryBase):
    """Schema for knowledge entry response"""
    id: str
    category_id: Optional[str] = None
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


class KnowledgeAttachmentBase(BaseModel):
    """Base schema for knowledge attachments"""
    filename: str
    content_type: str


class KnowledgeAttachmentCreate(KnowledgeAttachmentBase):
    """Schema for creating a knowledge attachment"""
    pass


class KnowledgeAttachmentResponse(KnowledgeAttachmentBase):
    """Schema for knowledge attachment response"""
    id: str
    knowledge_id: str
    original_filename: str
    size_bytes: int
    storage_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeRevisionBase(BaseModel):
    """Base schema for knowledge revisions"""
    title: str
    content: str
    summary: Optional[str] = None
    entry_metadata: Optional[Dict[str, Any]] = None


class KnowledgeRevisionResponse(KnowledgeRevisionBase):
    """Schema for knowledge revision response"""
    id: str
    knowledge_id: str
    version: int
    created_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Schema for search request"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    offset: int = 0


class SearchResponse(BaseModel):
    """Schema for search response"""
    results: List[KnowledgeEntryResponse]
    total: int
    query: str
