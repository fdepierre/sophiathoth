from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, JSON, Integer, Table
from sqlalchemy.orm import relationship
import datetime
import uuid

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


# Association table for many-to-many relationship between knowledge entries and tags
knowledge_tags = Table(
    "knowledge_tags",
    Base.metadata,
    Column("knowledge_id", String, ForeignKey("knowledge_entries.id")),
    Column("tag_id", String, ForeignKey("tags.id"))
)


class KnowledgeEntry(Base):
    """Model for knowledge entries"""
    __tablename__ = "knowledge_entries"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    source_type = Column(String, nullable=False)  # e.g., "tender", "manual", "imported"
    source_id = Column(String, nullable=True)  # Reference to source document if applicable
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    entry_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)
    
    # Relationships
    category_id = Column(String, ForeignKey("knowledge_categories.id"), nullable=True)
    category = relationship("KnowledgeCategory", back_populates="entries")
    tags = relationship("Tag", secondary=knowledge_tags, back_populates="knowledge_entries")
    attachments = relationship("KnowledgeAttachment", back_populates="knowledge_entry", cascade="all, delete-orphan")
    revisions = relationship("KnowledgeRevision", back_populates="knowledge_entry", cascade="all, delete-orphan")


class KnowledgeCategory(Base):
    """Model for knowledge categories"""
    __tablename__ = "knowledge_categories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(String, ForeignKey("knowledge_categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    entries = relationship("KnowledgeEntry", back_populates="category")
    children = relationship("KnowledgeCategory", backref="parent", remote_side=[id])


class Tag(Base):
    """Model for tags"""
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    knowledge_entries = relationship("KnowledgeEntry", secondary=knowledge_tags, back_populates="tags")


class KnowledgeAttachment(Base):
    """Model for knowledge attachments"""
    __tablename__ = "knowledge_attachments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    knowledge_id = Column(String, ForeignKey("knowledge_entries.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    knowledge_entry = relationship("KnowledgeEntry", back_populates="attachments")


class KnowledgeRevision(Base):
    """Model for knowledge revisions"""
    __tablename__ = "knowledge_revisions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    knowledge_id = Column(String, ForeignKey("knowledge_entries.id"), nullable=False)
    version = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    entry_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)
    
    # Relationships
    knowledge_entry = relationship("KnowledgeEntry", back_populates="revisions")
