from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class EmbeddingBase(BaseModel):
    """Base schema for embeddings"""
    text: str


class QuestionEmbeddingCreate(EmbeddingBase):
    """Schema for creating a question embedding"""
    question_id: str


class ResponseEmbeddingCreate(EmbeddingBase):
    """Schema for creating a response embedding"""
    response_id: str


class EmbeddingResponse(EmbeddingBase):
    """Schema for embedding response"""
    id: str
    embedding: List[float]
    model_name: str
    model_version: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionEmbeddingResponse(EmbeddingResponse):
    """Schema for question embedding response"""
    question_id: str


class ResponseEmbeddingResponse(EmbeddingResponse):
    """Schema for response embedding response"""
    response_id: str


class KnowledgeBaseCreate(BaseModel):
    """Schema for creating a knowledge base entry"""
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    confidence_score: Optional[float] = None


class KnowledgeBaseResponse(KnowledgeBaseCreate):
    """Schema for knowledge base response"""
    id: str
    embedding: List[float]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class SemanticCategoryCreate(BaseModel):
    """Schema for creating a semantic category"""
    name: str
    description: Optional[str] = None


class SemanticCategoryResponse(SemanticCategoryCreate):
    """Schema for semantic category response"""
    id: str
    embedding: List[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SimilarityRequest(BaseModel):
    """Schema for similarity request"""
    text: str
    limit: int = 5
    threshold: float = 0.7


class SimilarityResponse(BaseModel):
    """Schema for similarity response"""
    results: List[Dict[str, Any]]
    query_embedding: List[float]


class CategoryRequest(BaseModel):
    """Schema for category request"""
    text: str


class CategoryResponse(BaseModel):
    """Schema for category response"""
    category: str
    confidence: float


class GenerateResponseRequest(BaseModel):
    """Schema for generate response request"""
    question: str
    context: Optional[List[Dict[str, Any]]] = None
    max_tokens: int = 500


class GenerateResponseResponse(BaseModel):
    """Schema for generate response response"""
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
