from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize pgvector extension
def init_db():
    """Initialize database with required extensions"""
    try:
        # Create a connection
        conn = engine.connect()
        
        # Create pgvector extension if it doesn't exist
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute("COMMIT")
        
        logger.info("Database initialized with vector extension")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        conn.close()
