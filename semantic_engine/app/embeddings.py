from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from typing import List, Dict, Any, Union
import redis
import json
import spacy
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.models.embeddings import (
    QuestionEmbedding,
    ResponseEmbedding,
    KnowledgeBase,
    SemanticCategory
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.model = SentenceTransformer(self.model_name)
        self.model_version = self.model.get_sentence_embedding_dimension()
        
        # Initialize Redis for caching
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Load spaCy model for text preprocessing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text
        
        Args:
            text: The text to generate embedding for
            
        Returns:
            List of floats representing the embedding
        """
        # Check cache first
        cache_key = f"embedding:{hash(text)}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Preprocess text
        text = self._preprocess_text(text)
        
        # Generate embedding
        embedding = self.model.encode(text)
        
        # Convert to list and cache
        embedding_list = embedding.tolist()
        self.redis.set(cache_key, json.dumps(embedding_list), ex=3600)  # Cache for 1 hour
        
        return embedding_list
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for embedding
        
        Args:
            text: The text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Use spaCy for preprocessing
        doc = self.nlp(text)
        
        # Remove stopwords and punctuation, lemmatize
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        
        return " ".join(tokens)
    
    def create_question_embedding(self, db: Session, question_id: str, text: str) -> QuestionEmbedding:
        """
        Create embedding for a question
        
        Args:
            db: Database session
            question_id: ID of the question
            text: Text of the question
            
        Returns:
            Created QuestionEmbedding
        """
        embedding = self.generate_embedding(text)
        
        question_embedding = QuestionEmbedding(
            question_id=question_id,
            text=text,
            embedding=embedding,
            model_name=self.model_name,
            model_version=str(self.model_version)
        )
        
        db.add(question_embedding)
        db.commit()
        db.refresh(question_embedding)
        
        return question_embedding
    
    def create_response_embedding(self, db: Session, response_id: str, text: str) -> ResponseEmbedding:
        """
        Create embedding for a response
        
        Args:
            db: Database session
            response_id: ID of the response
            text: Text of the response
            
        Returns:
            Created ResponseEmbedding
        """
        embedding = self.generate_embedding(text)
        
        response_embedding = ResponseEmbedding(
            response_id=response_id,
            text=text,
            embedding=embedding,
            model_name=self.model_name,
            model_version=str(self.model_version)
        )
        
        db.add(response_embedding)
        db.commit()
        db.refresh(response_embedding)
        
        return response_embedding
    
    def create_knowledge_base_entry(
        self, 
        db: Session, 
        title: str, 
        content: str,
        category: str = None,
        tags: List[str] = None,
        source: str = None,
        confidence_score: float = None,
        created_by: str = None
    ) -> KnowledgeBase:
        """
        Create a knowledge base entry with embedding
        
        Args:
            db: Database session
            title: Title of the entry
            content: Content of the entry
            category: Optional category
            tags: Optional tags
            source: Optional source
            confidence_score: Optional confidence score
            created_by: Optional creator ID
            
        Returns:
            Created KnowledgeBase entry
        """
        # Generate embedding from title and content
        embedding_text = f"{title} {content}"
        embedding = self.generate_embedding(embedding_text)
        
        knowledge_base = KnowledgeBase(
            title=title,
            content=content,
            embedding=embedding,
            category=category,
            tags=tags,
            source=source,
            confidence_score=confidence_score,
            created_by=created_by
        )
        
        db.add(knowledge_base)
        db.commit()
        db.refresh(knowledge_base)
        
        return knowledge_base
    
    def create_semantic_category(
        self,
        db: Session,
        name: str,
        description: str = None
    ) -> SemanticCategory:
        """
        Create a semantic category with embedding
        
        Args:
            db: Database session
            name: Name of the category
            description: Optional description
            
        Returns:
            Created SemanticCategory
        """
        # Generate embedding from name and description
        embedding_text = f"{name} {description or ''}"
        embedding = self.generate_embedding(embedding_text)
        
        category = SemanticCategory(
            name=name,
            description=description,
            embedding=embedding
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        return category
    
    def find_similar_questions(
        self,
        db: Session,
        text: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar questions using vector similarity
        
        Args:
            db: Database session
            text: Query text
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar questions with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(text)
        
        # Convert to PostgreSQL array format
        embedding_array = f"ARRAY[{','.join(str(x) for x in query_embedding)}]"
        
        # Use pgvector to find similar questions
        query = text(f"""
            SELECT 
                id, 
                question_id, 
                text, 
                1 - (embedding <=> {embedding_array}::float[]) as similarity
            FROM 
                question_embeddings
            WHERE 
                1 - (embedding <=> {embedding_array}::float[]) > :threshold
            ORDER BY 
                similarity DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"threshold": threshold, "limit": limit})
        
        # Convert to list of dictionaries
        similar_questions = []
        for row in result:
            similar_questions.append({
                "id": row.id,
                "question_id": row.question_id,
                "text": row.text,
                "similarity": float(row.similarity)
            })
        
        return similar_questions
    
    def find_similar_knowledge(
        self,
        db: Session,
        text: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar knowledge base entries using vector similarity
        
        Args:
            db: Database session
            text: Query text
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar knowledge base entries with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(text)
        
        # Convert to PostgreSQL array format
        embedding_array = f"ARRAY[{','.join(str(x) for x in query_embedding)}]"
        
        # Use pgvector to find similar knowledge base entries
        query = text(f"""
            SELECT 
                id, 
                title,
                content,
                category,
                tags,
                source,
                1 - (embedding <=> {embedding_array}::float[]) as similarity
            FROM 
                knowledge_base
            WHERE 
                1 - (embedding <=> {embedding_array}::float[]) > :threshold
            ORDER BY 
                similarity DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"threshold": threshold, "limit": limit})
        
        # Convert to list of dictionaries
        similar_knowledge = []
        for row in result:
            similar_knowledge.append({
                "id": row.id,
                "title": row.title,
                "content": row.content,
                "category": row.category,
                "tags": row.tags,
                "source": row.source,
                "similarity": float(row.similarity)
            })
        
        return similar_knowledge
    
    def categorize_text(
        self,
        db: Session,
        text: str
    ) -> Dict[str, Any]:
        """
        Categorize text using semantic categories
        
        Args:
            db: Database session
            text: Text to categorize
            
        Returns:
            Dictionary with category and confidence
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(text)
        
        # Convert to PostgreSQL array format
        embedding_array = f"ARRAY[{','.join(str(x) for x in query_embedding)}]"
        
        # Use pgvector to find most similar category
        query = text(f"""
            SELECT 
                id, 
                name,
                description,
                1 - (embedding <=> {embedding_array}::float[]) as similarity
            FROM 
                semantic_categories
            ORDER BY 
                similarity DESC
            LIMIT 1
        """)
        
        result = db.execute(query).first()
        
        if not result:
            return {"category": "uncategorized", "confidence": 0.0}
        
        return {
            "category": result.name,
            "confidence": float(result.similarity)
        }


# Create a singleton instance
embedding_service = EmbeddingService()
