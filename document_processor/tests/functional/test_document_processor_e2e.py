import os
import sys
import unittest
import requests
import json
import pandas as pd
from pathlib import Path
import time

# Add the project root to the Python path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestDocumentProcessorE2E(unittest.TestCase):
    """End-to-end tests for the document processor"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Use a hardcoded port for testing
        cls.port = 8000
        cls.api_prefix = "/api/v1"
        cls.base_url = f"http://localhost:{cls.port}{cls.api_prefix}"
        cls.test_files_dir = Path(os.path.dirname(os.path.dirname(__file__)))
        
        # Check if the service is running
        try:
            response = requests.get(f"{cls.base_url}/health")
            if response.status_code != 200:
                print("Warning: Document processor service is not running or not responding")
        except requests.exceptions.ConnectionError:
            print("Warning: Document processor service is not running or not accessible")
        
        # Store uploaded document IDs for cleanup
        cls.document_ids = []
    
    def test_full_workflow(self):
        """Test the complete document processing workflow"""
        # Skip if service is not running
        try:
            requests.get(f"{self.base_url}/health")
        except requests.exceptions.ConnectionError:
            self.skipTest("Document processor service is not running")
        
        # Step 1: Upload both test files
        file_paths = [
            self.test_files_dir / "earth_question_answer.xlsx",
            self.test_files_dir / "test_question_answers.xlsx"
        ]
        
        for file_path in file_paths:
            self.assertTrue(file_path.exists(), f"Test file not found: {file_path}")
            
            # Upload the file
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                response = requests.post(f"{self.base_url}/documents/", files=files)
            
            # Verify the response
            self.assertEqual(response.status_code, 201, f"Upload failed: {response.text}")
            response_data = response.json()
            
            # Store document_id for later use and cleanup
            document_id = response_data["document_id"]
            self.document_ids.append(document_id)
            
            # Step 2: Verify document metadata
            response = requests.get(f"{self.base_url}/documents/{document_id}")
            self.assertEqual(response.status_code, 200)
            document_data = response.json()
            
            # Verify document properties
            self.assertEqual(document_data["original_filename"], file_path.name)
            self.assertIn("size_bytes", document_data)
            self.assertGreater(document_data["size_bytes"], 0)
            
            # Step 3: Verify sheets were extracted
            response = requests.get(f"{self.base_url}/documents/{document_id}/sheets")
            self.assertEqual(response.status_code, 200)
            sheets = response.json()
            self.assertGreater(len(sheets), 0)
            
            # Step 4: Verify questions were extracted
            response = requests.get(f"{self.base_url}/documents/{document_id}/questions")
            self.assertEqual(response.status_code, 200)
            questions = response.json()
            
            # There should be at least some questions in our test files
            self.assertGreater(len(questions), 0)
            
            # Step 5: Verify question structure
            for question in questions:
                self.assertIn("id", question)
                self.assertIn("text", question)
                self.assertIn("document_id", question)
                self.assertIn("sheet_id", question)
                self.assertEqual(question["document_id"], document_id)
    
    def test_api_error_handling(self):
        """Test API error handling"""
        # Skip if service is not running
        try:
            requests.get(f"{self.base_url}/health")
        except requests.exceptions.ConnectionError:
            self.skipTest("Document processor service is not running")
        
        # Test 1: Upload invalid file type
        with open(__file__, "rb") as f:
            files = {"file": ("test.py", f, "text/x-python")}
            response = requests.post(f"{self.base_url}/documents/", files=files)
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)
        
        # Test 2: Get non-existent document
        response = requests.get(f"{self.base_url}/documents/nonexistent-id")
        self.assertEqual(response.status_code, 404)
        
        # Test 3: Delete non-existent document
        response = requests.delete(f"{self.base_url}/documents/nonexistent-id")
        self.assertEqual(response.status_code, 404)
    
    def test_concurrent_uploads(self):
        """Test concurrent document uploads"""
        # Skip if service is not running
        try:
            requests.get(f"{self.base_url}/health")
        except requests.exceptions.ConnectionError:
            self.skipTest("Document processor service is not running")
        
        # Use the same file for multiple uploads
        file_path = self.test_files_dir / "test_question_answers.xlsx"
        self.assertTrue(file_path.exists(), f"Test file not found: {file_path}")
        
        # Upload the same file multiple times
        for _ in range(3):
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                response = requests.post(f"{self.base_url}/documents/", files=files)
            
            self.assertEqual(response.status_code, 201)
            document_id = response.json()["document_id"]
            self.document_ids.append(document_id)
        
        # Verify all documents were created with unique IDs
        response = requests.get(f"{self.base_url}/documents/")
        self.assertEqual(response.status_code, 200)
        documents = response.json()
        
        # Extract document IDs
        doc_ids = [doc["id"] for doc in documents]
        
        # Verify our uploaded documents are in the list
        for doc_id in self.document_ids:
            self.assertIn(doc_id, doc_ids)
        
        # Verify IDs are unique
        self.assertEqual(len(doc_ids), len(set(doc_ids)))
    
    def test_document_deletion(self):
        """Test document deletion"""
        # Skip if service is not running
        try:
            requests.get(f"{self.base_url}/health")
        except requests.exceptions.ConnectionError:
            self.skipTest("Document processor service is not running")
        
        # Upload a file
        file_path = self.test_files_dir / "test_question_answers.xlsx"
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(f"{self.base_url}/documents/", files=files)
        
        self.assertEqual(response.status_code, 201)
        document_id = response.json()["document_id"]
        
        # Delete the document
        response = requests.delete(f"{self.base_url}/documents/{document_id}")
        self.assertEqual(response.status_code, 204)
        
        # Verify document is deleted
        response = requests.get(f"{self.base_url}/documents/{document_id}")
        self.assertEqual(response.status_code, 404)
        
        # Verify sheets and questions are also deleted (cascade)
        response = requests.get(f"{self.base_url}/documents/{document_id}/sheets")
        self.assertEqual(response.status_code, 404)
        
        response = requests.get(f"{self.base_url}/documents/{document_id}/questions")
        self.assertEqual(response.status_code, 404)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Delete all uploaded documents
        for document_id in cls.document_ids:
            try:
                requests.delete(f"{cls.base_url}/documents/{document_id}")
            except:
                pass


if __name__ == "__main__":
    unittest.main()
