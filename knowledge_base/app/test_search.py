import asyncio
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.knowledge import KnowledgeEntry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search():
    """Test basic search functionality"""
    # Get database session
    db = next(get_db())
    
    try:
        # Try basic search
        query = "sample"
        logger.info(f"Searching for: {query}")
        
        # Basic text search
        entries = db.query(KnowledgeEntry).filter(
            KnowledgeEntry.title.ilike(f"%{query}%") | 
            KnowledgeEntry.content.ilike(f"%{query}%") |
            KnowledgeEntry.summary.ilike(f"%{query}%")
        ).all()
        
        logger.info(f"Found {len(entries)} entries")
        for entry in entries:
            logger.info(f"Entry: {entry.id} - {entry.title}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_search())
