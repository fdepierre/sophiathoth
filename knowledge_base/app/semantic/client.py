"""
Semantic client for knowledge base.
This module provides semantic search and similarity functionality.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeEntry
from app.semantic.service import semantic_service

logger = logging.getLogger(__name__)

class SemanticClient:
    """Client for semantic search and similarity operations."""
    
    def __init__(self):
        """Initialize the semantic client."""
        pass
    
    async def find_similar_knowledge(
        self,
        text: str,
        db: Session,
        limit: int = 10,
        threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Find knowledge entries similar to the given text.
        
        Args:
            text: Text to find similar entries for
            db: Database session
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar entries with their similarity scores
        """
        try:
            # Get all entries from database
            entries = db.query(KnowledgeEntry).all()
            
            # Convert entries to dictionaries
            entry_dicts = []
            for entry in entries:
                entry_dict = {
                    "id": entry.id,
                    "title": entry.title,
                    "content": entry.content,
                    "summary": entry.summary
                }
                entry_dicts.append(entry_dict)
            
            # Find similar entries
            similar_entries = semantic_service.find_similar_knowledge(
                text=text,
                entries=entry_dicts,
                limit=limit,
                threshold=threshold
            )
            
            return similar_entries
                    
        except Exception as e:
            logger.error(f"Error finding similar knowledge: {e}")
            return []
    
    async def categorize_text(self, text: str) -> Dict[str, Any]:
        """
        Categorize text using semantic analysis.
        
        Args:
            text: Text to categorize
            
        Returns:
            Dictionary with category and confidence score
        """
        try:
            return semantic_service.categorize_text(text)
                    
        except Exception as e:
            logger.error(f"Error categorizing text: {e}")
            return {"category": "uncategorized", "confidence": 0.0}

# Create a singleton instance
semantic_client = SemanticClient()
