import os
import unittest
import requests
import json
import pandas as pd
from pathlib import Path
from unittest.mock import patch

# Import the ExcelParser directly
from document_processor.app.parser import ExcelParser


class TestDocumentProcessor(unittest.TestCase):
    """Functional tests for the document processor"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Use a hardcoded port for testing
        cls.port = 8000
        cls.api_prefix = "/api/v1"
        cls.base_url = f"http://localhost:{cls.port}{cls.api_prefix}"
        cls.test_files_dir = Path(os.path.dirname(os.path.dirname(__file__)))
        cls.parser = ExcelParser()
        
        # Check if the service is running
        try:
            response = requests.get(f"{cls.base_url}/health")
            if response.status_code != 200:
                print("Warning: Document processor service is not running or not responding")
        except requests.exceptions.ConnectionError:
            print("Warning: Document processor service is not running or not accessible")
    
    def test_excel_parser_local(self):
        """Test the Excel parser directly without API"""
        # Test with earth_question_answer.xlsx
        file_path = self.test_files_dir / "earth_question_answer.xlsx"
        self.assertTrue(file_path.exists(), f"Test file not found: {file_path}")
        
        # Read the file content
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Parse the Excel file
        parsed_data = self.parser.parse_excel_file(file_content)
        
        # Verify the parsed data
        self.assertIn("sheets", parsed_data)
        self.assertIn("questions", parsed_data)
        self.assertIn("structure", parsed_data)
        
        # Verify sheets were parsed
        self.assertTrue(len(parsed_data["sheets"]) > 0)
        
        # Verify questions were extracted
        self.assertTrue(len(parsed_data["questions"]) > 0)
        
        # Verify structure information
        self.assertEqual(len(parsed_data["structure"]), len(parsed_data["sheets"]))
    
    def test_excel_parser_with_test_question_answers(self):
        """Test the Excel parser with test_question_answers.xlsx"""
        file_path = self.test_files_dir / "test_question_answers.xlsx"
        self.assertTrue(file_path.exists(), f"Test file not found: {file_path}")
        
        # Read the file content
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Parse the Excel file
        parsed_data = self.parser.parse_excel_file(file_content)
        
        # Verify the parsed data
        self.assertIn("sheets", parsed_data)
        self.assertIn("questions", parsed_data)
        
        # Verify specific content based on the test file
        # This assumes knowledge of the test file structure
        if "Sheet1" in parsed_data["sheets"]:
            sheet_data = parsed_data["sheets"]["Sheet1"]
            self.assertTrue(len(sheet_data) > 0, "Sheet1 should contain data")
            
            # Check if questions were properly extracted
            questions = [q for q in parsed_data["questions"] if q["sheet"] == "Sheet1"]
            self.assertTrue(len(questions) > 0, "Should extract questions from Sheet1")
    
    @patch('document_processor.app.storage.minio_client')
    def test_api_upload_document(self, mock_minio):
        """Test document upload API endpoint with MinIO mocked"""
        # Configure the mock
        mock_upload_filename = "mock_uuid_filename.xlsx"
        mock_minio.upload_file.return_value = mock_upload_filename
        
        # Skip if service is not running
        try:
            requests.get(f"{self.base_url}/health")
        except requests.exceptions.ConnectionError:
            self.skipTest("Document processor service is not running")
        
        # Test with earth_question_answer.xlsx
        file_path = self.test_files_dir / "earth_question_answer.xlsx"
        self.assertTrue(file_path.exists(), f"Test file not found: {file_path}")
        
        # Upload the file
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(f"{self.base_url}/documents/", files=files)
        
        # Verify the response indicates success
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("document_id", response_data)
        self.assertIn("filename", response_data)
        self.assertIn("storage_path", response_data)
        self.assertEqual(response_data["storage_path"], mock_upload_filename) # Check if mocked path is returned
        
        # Optionally, verify the mock was called as expected
        mock_minio.upload_file.assert_called_once()
        # You could add more specific call argument checks if needed
        
        # Store document_id for cleanup
        self.document_id = response_data["document_id"]
        
        # Test retrieving the document
        response = requests.get(f"{self.base_url}/documents/{self.document_id}")
        self.assertEqual(response.status_code, 200)
        
        # Test retrieving sheets
        response = requests.get(f"{self.base_url}/documents/{self.document_id}/sheets")
        self.assertEqual(response.status_code, 200)
        sheets = response.json()
        self.assertEqual(len(sheets), response_data["sheet_count"])
        
        # Test retrieving questions
        response = requests.get(f"{self.base_url}/documents/{self.document_id}/questions")
        self.assertEqual(response.status_code, 200)
        questions = response.json()
        self.assertEqual(len(questions), response_data["question_count"])
    
    def test_question_extraction_accuracy(self):
        """Test the accuracy of question extraction"""
        # Test with test_question_answers.xlsx which has known questions
        file_path = self.test_files_dir / "test_question_answers.xlsx"
        
        # Read the Excel file directly to verify questions
        df = pd.read_excel(file_path)
        
        # Get questions from the dataframe (cells ending with ?)
        expected_questions = []
        for i, row in df.iterrows():
            for col in df.columns:
                cell_value = str(row[col])
                if cell_value.strip().endswith('?'):
                    expected_questions.append(cell_value.strip())
        
        # Parse with our parser
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        parsed_data = self.parser.parse_excel_file(file_content)
        extracted_questions = [q["text"].strip() for q in parsed_data["questions"]]
        
        # Verify all expected questions were found
        for question in expected_questions:
            self.assertIn(question, extracted_questions, f"Question not extracted: {question}")
    
    def tearDown(self):
        """Clean up after tests"""
        # Delete uploaded document if it exists
        if hasattr(self, 'document_id'):
            try:
                requests.delete(f"{self.base_url}/documents/{self.document_id}")
            except:
                pass


if __name__ == "__main__":
    unittest.main()
