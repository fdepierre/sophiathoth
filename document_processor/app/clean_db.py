"""
Database cleanup script for Document Processor Service.
This script removes all data from the database tables.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import (
    Base, TenderDocument, TenderSheet, TenderQuestion, TenderResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_db() -> None:
    """Clean the database by removing all data from all tables."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info("Cleaning document processor database...")
        
        # Delete all entries in the correct order to respect foreign key constraints
        logger.info("Deleting tender responses...")
        db.query(TenderResponse).delete()
        
        logger.info("Deleting tender questions...")
        db.query(TenderQuestion).delete()
        
        logger.info("Deleting tender sheets...")
        db.query(TenderSheet).delete()
        
        logger.info("Deleting tender documents...")
        db.query(TenderDocument).delete()
        
        # Commit the changes
        db.commit()
        logger.info("Document processor database cleaned successfully.")
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
