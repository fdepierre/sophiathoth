from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.api import api_router
from app.config import settings
from app.database import get_db, Base, engine

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Knowledge Base Service",
    description="API for managing knowledge base entries for the Tender Management System",
    version="0.1.0",
)

# Configure CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    """
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check MinIO connection
    try:
        from app.storage import minio_client
        minio_client._ensure_bucket_exists()
        minio_status = "healthy"
    except Exception as e:
        logger.error(f"MinIO health check failed: {e}")
        minio_status = "unhealthy"
    
    # Check Redis connection
    try:
        from app.semantic import semantic_client
        semantic_client.redis.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"
    
    return {
        "status": "ok" if all(s == "healthy" for s in [db_status, minio_status, redis_status]) else "degraded",
        "version": settings.VERSION,
        "components": {
            "database": db_status,
            "minio": minio_status,
            "redis": redis_status
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
