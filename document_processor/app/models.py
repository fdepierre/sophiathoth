from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
import datetime
import uuid

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class TenderDocument(Base):
    """Model for tender documents"""
    __tablename__ = "tender_documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    doc_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)
    
    # Relationships
    sheets = relationship("TenderSheet", back_populates="document", cascade="all, delete-orphan")
    questions = relationship("TenderQuestion", back_populates="document", cascade="all, delete-orphan")


class TenderSheet(Base):
    """Model for tender document sheets"""
    __tablename__ = "tender_sheets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("tender_documents.id"), nullable=False)
    name = Column(String, nullable=False)
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    headers = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("TenderDocument", back_populates="sheets")
    questions = relationship("TenderQuestion", back_populates="sheet", cascade="all, delete-orphan")


class TenderQuestion(Base):
    """Model for tender questions"""
    __tablename__ = "tender_questions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("tender_documents.id"), nullable=False)
    sheet_id = Column(String, ForeignKey("tender_sheets.id"), nullable=False)
    text = Column(Text, nullable=False)
    row_index = Column(Integer, nullable=True)
    column_index = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    context = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("TenderDocument", back_populates="questions")
    sheet = relationship("TenderSheet", back_populates="questions")
    responses = relationship("TenderResponse", back_populates="question", cascade="all, delete-orphan")


class TenderResponse(Base):
    """Model for tender responses"""
    __tablename__ = "tender_responses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    question_id = Column(String, ForeignKey("tender_questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    source_reference = Column(String, nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)
    
    # Relationships
    question = relationship("TenderQuestion", back_populates="responses")
