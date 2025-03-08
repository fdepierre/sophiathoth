from fastapi import APIRouter

from app.api.routes import categories, tags, knowledge

api_router = APIRouter()

# Include routers from different modules
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(knowledge.router, prefix="/entries", tags=["knowledge"])
