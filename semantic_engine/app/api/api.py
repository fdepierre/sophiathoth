from fastapi import APIRouter
from app.api.routes import embeddings, knowledge, llm

api_router = APIRouter()

api_router.include_router(
    embeddings.router,
    prefix="/embeddings",
    tags=["embeddings"]
)

api_router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["knowledge"]
)

api_router.include_router(
    llm.router,
    prefix="/llm",
    tags=["llm"]
)
