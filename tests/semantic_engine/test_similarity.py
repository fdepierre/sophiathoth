import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session 
from typing import Generator
from unittest.mock import patch, MagicMock 
import numpy as np 

from semantic_engine.app.embeddings import EmbeddingService
from semantic_engine.app.models.embeddings import Base 
from semantic_engine.app.config import settings

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="module")
def embedding_service() -> EmbeddingService:
    dummy_embedding = np.random.rand(settings.EMBEDDING_DIMENSION).tolist()
    
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"embedding": dummy_embedding}
    
    with patch('semantic_engine.app.embeddings.requests.post', return_value=mock_response) as mock_post:
        service = EmbeddingService()
        service._mock_post = mock_post 
        yield service

def test_generate_embedding(embedding_service: EmbeddingService):
    text = "This is a test sentence."
    embedding = embedding_service.generate_embedding(text)
    
    embedding_service._mock_post.assert_called_once()
    call_args = embedding_service._mock_post.call_args
    assert call_args[1]['json']['prompt'] == text
    assert call_args[1]['json']['model'] == settings.OLLAMA_MODEL
    
    assert isinstance(embedding, list)
    assert len(embedding) == settings.EMBEDDING_DIMENSION 
    assert all(isinstance(val, float) for val in embedding)
    assert embedding == embedding_service._mock_post.return_value.json.return_value['embedding']

# TODO: Add test cases for creating embeddings in the DB
# - test_create_question_embedding
# - test_create_response_embedding
# - test_create_knowledge_embedding
# These tests would use the db_session fixture and assert DB state.

# TODO: Add test cases for edge conditions for generate_embedding
# - Empty input text
# - Invalid input type

# NOTE: Similarity tests removed as the service methods are commented out.
# Future tests for similarity search will need to consider:
# - Mocking the database query (if not using a real test DB with pgvector)
# - Handling vector normalization if required by the chosen similarity metric.
