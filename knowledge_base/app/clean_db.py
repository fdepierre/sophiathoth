"""
Database cleanup script for Knowledge Base Service.
This script removes all data from the database tables.
"""

import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.knowledge import (
    Base, KnowledgeEntry, KnowledgeCategory, Tag, 
    KnowledgeAttachment, KnowledgeRevision, knowledge_tags
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_db() -> None:
    """Clean the database by removing all data from all tables."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info("Cleaning knowledge base database...")
        
        # Delete all entries in the correct order to respect foreign key constraints
        logger.info("Deleting knowledge revisions...")
        db.query(KnowledgeRevision).delete()
        
        logger.info("Deleting knowledge attachments...")
        db.query(KnowledgeAttachment).delete()
        
        logger.info("Clearing knowledge_tags association table...")
        db.execute(knowledge_tags.delete())
        
        logger.info("Deleting knowledge entries...")
        db.query(KnowledgeEntry).delete()
        
        logger.info("Deleting tags...")
        db.query(Tag).delete()
        
        logger.info("Deleting knowledge categories...")
        db.query(KnowledgeCategory).delete()
        
        # Commit the changes
        db.commit()
        logger.info("Knowledge base database cleaned successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting database cleanup...")
    clean_db()
    logger.info("Database cleanup completed.")
