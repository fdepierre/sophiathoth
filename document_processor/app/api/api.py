from fastapi import APIRouter
from app.api.routes import documents, questions

api_router = APIRouter()

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    questions.router,
    prefix="/questions",
    tags=["questions"]
)
