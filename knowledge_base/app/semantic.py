import httpx
import logging
from typing import List, Dict, Any, Optional
import json
import redis

from app.config import settings

logger = logging.getLogger(__name__)


class SemanticClient:
    """Client for interacting with the Semantic Engine service"""
    
    def __init__(self):
        self.base_url = settings.SEMANTIC_ENGINE_URL
        
        # Initialize Redis for caching
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    async def find_similar_knowledge(
        self,
        text: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar knowledge using the Semantic Engine
        
        Args:
            text: Query text
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar knowledge with similarity scores
        """
        # Check cache first
        cache_key = f"similar_knowledge:{hash(text)}:{limit}:{threshold}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/embeddings/similar-knowledge",
                    json={
                        "text": text,
                        "limit": limit,
                        "threshold": threshold
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Cache the results
                self.redis.set(cache_key, json.dumps(result["results"]), ex=self.cache_ttl)
                
                return result["results"]
        
        except Exception as e:
            logger.error(f"Error finding similar knowledge: {e}")
            return []
    
    async def categorize_text(self, text: str) -> Dict[str, Any]:
        """
        Categorize text using the Semantic Engine
        
        Args:
            text: Text to categorize
            
        Returns:
            Dictionary with category and confidence
        """
        # Check cache first
        cache_key = f"categorize:{hash(text)}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/knowledge/categorize",
                    json={"text": text},
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Cache the results
                self.redis.set(cache_key, json.dumps(result), ex=self.cache_ttl)
                
                return result
        
        except Exception as e:
            logger.error(f"Error categorizing text: {e}")
            return {"category": "uncategorized", "confidence": 0.0}
    
    async def generate_response(
        self,
        question: str,
        context: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Generate a response using the Semantic Engine
        
        Args:
            question: The question to answer
            context: Optional context for the question
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary with response, sources, and confidence
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/llm/generate-response",
                    json={
                        "question": question,
                        "context": context,
                        "max_tokens": max_tokens
                    },
                    timeout=60.0
                )
                
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I'm sorry, I encountered an error while generating a response.",
                "sources": [],
                "confidence": 0.0
            }


# Create a singleton instance
semantic_client = SemanticClient()
