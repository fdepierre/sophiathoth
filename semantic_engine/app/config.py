from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://tender_user:password@postgres:5432/tender_db"
    )
    
    # API settings
    API_V1_STR: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="Tender Management System - Semantic Engine")
    
    # Embedding model settings
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = Field(default=384)  # Dimension for the chosen model
    
    # Redis settings
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    # Ollama settings
    OLLAMA_BASE_URL: str = Field(default="http://ollama:11434")
    OLLAMA_MODEL: str = Field(default="llama2")
    
    # Document processor service
    DOCUMENT_PROCESSOR_URL: str = Field(default="http://document_processor:8000/api/v1")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(default=["*"])
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
