from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://tender_user:password@postgres:5432/tender_db"
    )
    
    # MinIO settings
    MINIO_ENDPOINT: str = Field(default="minio:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_SECURE: bool = Field(default=False)
    MINIO_BUCKET_NAME: str = Field(default="tender-documents")
    
    # API settings
    API_V1_STR: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="Tender Management System - Document Processor")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
