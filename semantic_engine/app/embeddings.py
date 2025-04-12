from sqlalchemy.orm import Session
from sqlalchemy import text
from tenacity import retry, stop_after_attempt, wait_fixed
import numpy as np
import logging
from typing import List, Dict, Any, Union
import redis
import json
import requests
from app.config import settings
from app.models.embeddings import (
    QuestionEmbedding,
    ResponseEmbedding,
    KnowledgeBase,
    SemanticCategory
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings via Ollama"""
    
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.embedding_dimension = settings.EMBEDDING_DIMENSION
        
        # Initialize Redis for caching (if needed, otherwise can be removed)
        # Consider if caching is still useful/relevant with Ollama
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=1 # Quick check
            )
            self.redis.ping() # Check connection
            logger.info("Redis connection successful.")
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text using the Ollama API.
        Handles potential API errors and retries.
        """
        if not text or not isinstance(text, str):
            logger.error("Invalid text input for embedding generation.")
            return [0.0] * self.embedding_dimension # Return zero vector for invalid input
            
        ollama_api_url = f"{self.ollama_base_url}/api/embeddings"
        payload = {
            "model": self.ollama_model,
            "prompt": text
        }
        headers = {"Content-Type": "application/json"}
        
        try:
            logger.debug(f"Sending request to Ollama: {ollama_api_url} with model {self.ollama_model}")
            response = requests.post(ollama_api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            result = response.json()
            embedding = result.get("embedding")
            
            if embedding and isinstance(embedding, list) and len(embedding) == self.embedding_dimension:
                 # Optional: Normalize the embedding if needed for cosine similarity
                 # embedding_np = np.array(embedding)
                 # norm = np.linalg.norm(embedding_np)
                 # if norm == 0:
                 #    return embedding # Avoid division by zero
                 # normalized_embedding = (embedding_np / norm).tolist()
                 # return normalized_embedding
                return embedding
            else:
                logger.error(f"Ollama API returned unexpected embedding format or dimension. Expected {self.embedding_dimension}, got {len(embedding) if embedding else 'None'}. Result: {result}")
                return [0.0] * self.embedding_dimension # Return zero vector on format error

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API at {ollama_api_url}: {e}")
            raise  # Re-raise the exception to trigger tenacity retry
        except Exception as e:
             logger.error(f"An unexpected error occurred during embedding generation: {e}")
             # Depending on policy, might return zero vector or raise
             return [0.0] * self.embedding_dimension 

    def _preprocess_text(self, text: str) -> str:
        """Basic text preprocessing (can be expanded)."""
        text = text.strip()
        # Add more steps if needed (e.g., lowercasing, removing punctuation)
        return text

    def create_question_embedding(
        self, 
        db: Session, 
        question_id: int, 
        text: str, 
        category_name: str = None
    ) -> QuestionEmbedding:
        """
        Create and store a question embedding.
        Preprocesses text before generating embedding.
        """
        processed_text = self._preprocess_text(text)
        embedding_vector = self.generate_embedding(processed_text)
        
        db_embedding = QuestionEmbedding(
            question_id=question_id,
            text=processed_text, # Store processed text
            embedding=embedding_vector,
            model_version=f"ollama-{self.ollama_model}",
            category_name=category_name
        )
        db.add(db_embedding)
        db.commit()
        db.refresh(db_embedding)
        logger.info(f"Created embedding for question_id: {question_id}")
        return db_embedding

    def create_response_embedding(
        self, 
        db: Session, 
        response_id: int, 
        text: str, 
        category_name: str = None
    ) -> ResponseEmbedding:
        """
        Create and store a response embedding.
        Preprocesses text before generating embedding.
        """
        processed_text = self._preprocess_text(text)
        embedding_vector = self.generate_embedding(processed_text)
        
        db_embedding = ResponseEmbedding(
            response_id=response_id,
            text=processed_text, # Store processed text
            embedding=embedding_vector,
            model_version=f"ollama-{self.ollama_model}",
            category_name=category_name
        )
        db.add(db_embedding)
        db.commit()
        db.refresh(db_embedding)
        logger.info(f"Created embedding for response_id: {response_id}")
        return db_embedding

    def create_knowledge_embedding(
        self, 
        db: Session, 
        kb_id: int, 
        text: str, 
        category_name: str = None
    ) -> KnowledgeBase:
        """
        Create and store a knowledge base entry embedding.
        Preprocesses text before generating embedding.
        """
        processed_text = self._preprocess_text(text)
        embedding_vector = self.generate_embedding(processed_text)
        
        db_embedding = KnowledgeBase(
            kb_id=kb_id,
            text=processed_text, # Store processed text
            embedding=embedding_vector,
            model_version=f"ollama-{self.ollama_model}",
            category_name=category_name
        )
        db.add(db_embedding)
        db.commit()
        db.refresh(db_embedding)
        logger.info(f"Created embedding for kb_id: {kb_id}")
        return db_embedding

    # NOTE: Similarity search methods removed for now due to potential 
    # normalization issues with Ollama embeddings and pgvector operators.
    # These need to be re-evaluated based on the chosen similarity metric 
    # (e.g., cosine similarity with explicit normalization, dot product, etc.)

    # def find_similar_questions(self, db: Session, text: str, top_n: int = 5) -> List[Dict[str, Any]]:
    #     ...

    # def find_similar_responses(self, db: Session, text: str, top_n: int = 5) -> List[Dict[str, Any]]:
    #     ...
    
    # def find_similar_knowledge(self, db: Session, text: str, top_n: int = 5) -> List[Dict[str, Any]]:
    #    ...

# Create a singleton instance
embedding_service = EmbeddingService()
