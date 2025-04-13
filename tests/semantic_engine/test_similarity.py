import pytest
import os
import numpy as np
import pandas as pd
import json
import requests
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session 
from typing import Generator, List, Dict, Any
from unittest.mock import patch, MagicMock 

from semantic_engine.app.embeddings import EmbeddingService
from semantic_engine.app.models.embeddings import Base, QuestionEmbedding, ResponseEmbedding 
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

@pytest.fixture(scope="module")
def excel_data():
    """Fixture to load and provide test data from Excel files"""
    # Path to test files - navigate up from current directory to find test data
    test_dir = Path(__file__).parent.parent.parent
    test_excel_file = test_dir / "tests" / "earth_question_answer.xlsx"
    
    # Skip if file doesn't exist
    if not test_excel_file.exists():
        pytest.skip(f"Test file not found: {test_excel_file}")
    
    # Load Excel data
    df_dict = pd.read_excel(test_excel_file, sheet_name=None)
    questions = []
    answers = []
    
    # Extract questions and answers from Excel
    for sheet_name, df in df_dict.items():
        for i, row in df.iterrows():
            # Assuming first column is question, second column is answer
            if len(df.columns) >= 2:
                question = str(row[df.columns[0]]).strip()
                answer = str(row[df.columns[1]]).strip()
                if question.endswith('?'):
                    questions.append(question)
                    answers.append(answer)
    
    return {
        "questions": questions,
        "answers": answers
    }

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

def test_create_question_embeddings_from_excel(db_session: Session, embedding_service: EmbeddingService, excel_data):
    """Test creating embeddings for questions from Excel file"""
    # Verify we have questions
    assert len(excel_data["questions"]) > 0, "No questions found in test data"
    
    # Process the first 5 questions (or all if fewer than 5)
    questions = excel_data["questions"][:5]
    
    # Create embeddings for questions
    for i, question in enumerate(questions):
        # Reset the mock for each call
        embedding_service._mock_post.reset_mock()
        
        # Generate dummy embedding for this call
        dummy_embedding = np.random.rand(settings.EMBEDDING_DIMENSION).tolist()
        embedding_service._mock_post.return_value.json.return_value = {"embedding": dummy_embedding}
        
        # Create question embedding in DB
        db_embedding = embedding_service.create_question_embedding(
            db=db_session,
            question_id=i+1,  # Use index as question ID
            text=question
        )
        
        # Verify the API call
        embedding_service._mock_post.assert_called_once()
        call_args = embedding_service._mock_post.call_args
        assert call_args[1]['json']['prompt'] == question
        
        # Verify the database entry
        assert db_embedding.question_id == i+1
        assert db_embedding.text == question
        assert db_embedding.embedding == dummy_embedding
        assert db_embedding.model_version == f"ollama-{settings.OLLAMA_MODEL}"
        
        # Print confirmation
        print(f"Created embedding for question: {question[:50]}...")

def test_create_answer_embeddings_from_excel(db_session: Session, embedding_service: EmbeddingService, excel_data):
    """Test creating embeddings for answers from Excel file"""
    # Verify we have answers
    assert len(excel_data["answers"]) > 0, "No answers found in test data"
    
    # Process the first 5 answers (or all if fewer than 5)
    answers = excel_data["answers"][:5]
    
    # Create embeddings for answers
    for i, answer in enumerate(answers):
        # Reset the mock for each call
        embedding_service._mock_post.reset_mock()
        
        # Generate dummy embedding for this call
        dummy_embedding = np.random.rand(settings.EMBEDDING_DIMENSION).tolist()
        embedding_service._mock_post.return_value.json.return_value = {"embedding": dummy_embedding}
        
        # Create response embedding in DB
        db_embedding = embedding_service.create_response_embedding(
            db=db_session,
            response_id=i+1,  # Use index as response ID
            text=answer
        )
        
        # Verify the API call
        embedding_service._mock_post.assert_called_once()
        call_args = embedding_service._mock_post.call_args
        assert call_args[1]['json']['prompt'] == answer
        
        # Verify the database entry
        assert db_embedding.response_id == i+1
        assert db_embedding.text == answer
        assert db_embedding.embedding == dummy_embedding
        assert db_embedding.model_version == f"ollama-{settings.OLLAMA_MODEL}"
        
        # Print confirmation
        print(f"Created embedding for answer: {answer[:50]}...")

def test_cosine_similarity_calculation():
    """Test calculating cosine similarity between vectors"""
    # Function to calculate cosine similarity
    def cosine_similarity(vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    # Create some test vectors
    vec1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    vec2 = np.array([0.5, 0.4, 0.3, 0.2, 0.1])
    vec3 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])  # Same as vec1
    
    # Calculate similarities
    sim1_2 = cosine_similarity(vec1, vec2)
    sim1_3 = cosine_similarity(vec1, vec3)
    
    # Verify similarities
    assert sim1_2 < 1.0  # Different vectors should have similarity < 1
    assert pytest.approx(sim1_3, 1e-6) == 1.0  # Same vectors should have similarity = 1
    
    print(f"Similarity between different vectors: {sim1_2}")
    print(f"Similarity between identical vectors: {sim1_3}")
    
    # Test with real-world question embedding dimensions (384)
    vec4 = np.random.rand(384)
    vec5 = np.random.rand(384)
    sim4_5 = cosine_similarity(vec4, vec5)
    
    # Verify the similarity is between -1 and 1
    assert sim4_5 > -1.0
    assert sim4_5 < 1.0
    
    print(f"Similarity between random 384-dim vectors: {sim4_5}")

# Mock implementation of find_similar function for testing
def test_mock_similarity_search(embedding_service: EmbeddingService, excel_data):
    """Test mocked implementation of similarity search"""
    # Verify we have questions
    assert len(excel_data["questions"]) > 0, "No questions found in test data"
    
    # Use first question as query
    query = excel_data["questions"][0]
    
    # Define a mock implementation of find_similar_questions
    def mock_find_similar(text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        # Use other questions as potential matches
        matches = []
        questions = excel_data["questions"][1:6]  # Skip the query question
        
        # Generate random similarity scores
        for i, q in enumerate(questions):
            # Higher score for first match, descending thereafter
            similarity = 0.95 - (i * 0.05)
            matches.append({
                "id": f"q-{i+1}",
                "text": q,
                "similarity": similarity
            })
        
        return matches
    
    # Patch the find_similar_questions method
    with patch.object(embedding_service, 'find_similar_questions', side_effect=mock_find_similar):
        # Perform similarity search
        results = embedding_service.find_similar_questions(text=query, limit=5, threshold=0.7)
        
        # Verify we got results
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Verify result format
        for result in results:
            assert "id" in result
            assert "text" in result
            assert "similarity" in result
            assert 0 <= result["similarity"] <= 1
        
        # Results should be sorted by similarity (highest first)
        similarities = [r["similarity"] for r in results]
        assert similarities == sorted(similarities, reverse=True)
        
        # Print results
        print(f"Query: {query}")
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result['text'][:50]}... (Similarity: {result['similarity']})")
