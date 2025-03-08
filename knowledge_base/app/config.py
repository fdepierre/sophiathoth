from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os
from typing import Optional, List, Union
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings"""
    
    # API settings
    API_V1_STR: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="Tender Management System - Knowledge Base")
    VERSION: str = Field(default="0.1.0")
    DEBUG: bool = Field(default=False)
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://tender_user:password@postgres:5432/tender_db"
    )
    
    # MinIO settings
    MINIO_ENDPOINT: str = Field(default="minio:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_SECURE: bool = Field(default=False)
    MINIO_BUCKET_NAME: str = Field(default="tender-knowledge")
    
    # Redis settings
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=1)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    # Semantic engine service
    SEMANTIC_ENGINE_URL: str = Field(default="http://semantic_engine:8000/api/v1")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = Field(default=["*"])
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
