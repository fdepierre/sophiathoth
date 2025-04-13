"""
Semantic service for knowledge base.
This module provides semantic search and similarity functionality.
"""
import os
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class SemanticService:
    """Service for semantic search and similarity operations."""
    
    def __init__(self):
        """Initialize the semantic service."""
        # Use a simple model that doesn't require authentication
        self.model = SentenceTransformer('distilbert-base-nli-mean-tokens')
        self.embeddings_cache = {}
    
    def find_similar_knowledge(
        self,
        text: str,
        entries: List[Dict[str, Any]],
        limit: int = 10,
        threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Find knowledge entries similar to the given text.
        
        Args:
            text: Text to find similar entries for
            entries: List of knowledge entries to search through
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar entries with their similarity scores
        """
        try:
            # Get text embedding
            text_embedding = self.model.encode(text, convert_to_tensor=True)
            
            # Get embeddings for entries
            entry_embeddings = []
            for entry in entries:
                entry_text = f"{entry['title']} {entry['summary']} {entry['content']}"
                entry_embedding = self.model.encode(entry_text, convert_to_tensor=True)
                entry_embeddings.append(entry_embedding)
            
            # Calculate similarities
            similarities = []
            for i, entry_embedding in enumerate(entry_embeddings):
                similarity = np.dot(text_embedding, entry_embedding) / (
                    np.linalg.norm(text_embedding) * np.linalg.norm(entry_embedding)
                )
                if similarity >= threshold:
                    similarities.append((similarity, i))
            
            # Sort by similarity and get top results
            similarities.sort(reverse=True)
            top_similarities = similarities[:limit]
            
            # Create result list
            results = []
            for similarity, index in top_similarities:
                entry = entries[index]
                results.append({
                    "id": entry["id"],
                    "title": entry["title"],
                    "summary": entry["summary"],
                    "similarity": float(similarity)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar knowledge: {e}")
            return []
    
    def categorize_text(self, text: str) -> Dict[str, Any]:
        """
        Categorize text using semantic analysis.
        
        Args:
            text: Text to categorize
            
        Returns:
            Dictionary with category and confidence score
        """
        try:
            # For now, just return uncategorized
            return {"category": "uncategorized", "confidence": 0.0}
            
        except Exception as e:
            logger.error(f"Error categorizing text: {e}")
            return {"category": "uncategorized", "confidence": 0.0}

# Create a singleton instance
semantic_service = SemanticService()
