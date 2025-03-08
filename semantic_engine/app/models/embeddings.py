from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
import datetime
import uuid

from app.database import Base
from app.config import settings


def generate_uuid():
    return str(uuid.uuid4())


class QuestionEmbedding(Base):
    """Model for question embeddings"""
    __tablename__ = "question_embeddings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    question_id = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class ResponseEmbedding(Base):
    """Model for response embeddings"""
    __tablename__ = "response_embeddings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    response_id = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class KnowledgeBase(Base):
    """Model for knowledge base entries"""
    __tablename__ = "knowledge_base"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    category = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    source = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)


class SemanticCategory(Base):
    """Model for semantic categories"""
    __tablename__ = "semantic_categories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    embedding = Column(ARRAY(Float), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
