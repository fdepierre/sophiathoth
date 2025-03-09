from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class TenderDocumentBase(BaseModel):
    """Base schema for tender documents"""
    filename: str
    content_type: str


class TenderDocumentCreate(TenderDocumentBase):
    """Schema for creating a tender document"""
    pass


class TenderDocumentResponse(TenderDocumentBase):
    """Schema for tender document response"""
    id: str
    original_filename: str
    size_bytes: int
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenderSheetBase(BaseModel):
    """Base schema for tender sheets"""
    name: str
    row_count: int
    column_count: int
    headers: Optional[List[str]] = None


class TenderSheetResponse(TenderSheetBase):
    """Schema for tender sheet response"""
    id: str
    document_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenderQuestionBase(BaseModel):
    """Base schema for tender questions"""
    text: str
    row_index: Optional[int] = None
    column_index: Optional[int] = None
    category: Optional[str] = None
    context: Optional[str] = None


class TenderQuestionCreate(TenderQuestionBase):
    """Schema for creating a tender question"""
    sheet_id: str


class TenderQuestionResponse(TenderQuestionBase):
    """Schema for tender question response"""
    id: str
    document_id: str
    sheet_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenderResponseBase(BaseModel):
    """Base schema for tender responses"""
    text: str
    source_reference: Optional[str] = None
    confidence_score: Optional[int] = None


class TenderResponseCreate(TenderResponseBase):
    """Schema for creating a tender response"""
    question_id: str


class TenderResponseUpdate(BaseModel):
    """Schema for updating a tender response"""
    text: Optional[str] = None
    is_approved: Optional[bool] = None
    approved_by: Optional[str] = None


class TenderResponseResponse(TenderResponseBase):
    """Schema for tender response response"""
    id: str
    question_id: str
    is_approved: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class ParsedExcelResponse(BaseModel):
    """Schema for parsed Excel response"""
    document_id: str
    sheet_count: int
    question_count: int
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
