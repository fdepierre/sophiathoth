import os
import unittest
import pandas as pd
from pathlib import Path


class TestExcelParser(unittest.TestCase):
    """Functional tests for Excel parsing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_files_dir = Path(os.path.dirname(os.path.dirname(__file__)))
        self.test_files = [
            self.test_files_dir / "earth_question_answer.xlsx",
            self.test_files_dir / "test_question_answers.xlsx"
        ]
        
        # Verify test files exist
        for file_path in self.test_files:
            self.assertTrue(file_path.exists(), f"Test file not found: {file_path}")
    
    def test_excel_file_loading(self):
        """Test loading Excel files with pandas"""
        for file_path in self.test_files:
            # Read the Excel file
            df_dict = pd.read_excel(file_path, sheet_name=None)
            
            # Verify we can read the Excel file
            self.assertIsInstance(df_dict, dict)
            self.assertTrue(len(df_dict) > 0, f"No sheets found in {file_path}")
            
            # Print some information about the file
            print(f"\nFile: {file_path.name}")
            print(f"Number of sheets: {len(df_dict)}")
            
            for sheet_name, df in df_dict.items():
                print(f"  Sheet: {sheet_name}, Rows: {len(df)}, Columns: {len(df.columns)}")
                
                # Check for potential questions (cells ending with ?)
                question_count = 0
                for i, row in df.iterrows():
                    for col in df.columns:
                        cell_value = str(row[col])
                        if cell_value.strip().endswith('?'):
                            question_count += 1
                
                print(f"  Potential questions found: {question_count}")
    
    def test_question_extraction(self):
        """Test extracting questions from Excel files"""
        for file_path in self.test_files:
            # Read the Excel file
            df_dict = pd.read_excel(file_path, sheet_name=None)
            
            # Extract questions (cells ending with ?)
            questions = []
            for sheet_name, df in df_dict.items():
                for i, row in df.iterrows():
                    for col in df.columns:
                        cell_value = str(row[col])
                        if cell_value.strip().endswith('?'):
                            questions.append({
                                "sheet": sheet_name,
                                "row": i,
                                "column": col,
                                "text": cell_value.strip()
                            })
            
            # Verify questions were found
            self.assertTrue(len(questions) > 0, f"No questions found in {file_path}")
            
            # Print the questions
            print(f"\nFile: {file_path.name}")
            print(f"Questions found: {len(questions)}")
            for i, q in enumerate(questions[:5]):  # Show first 5 questions
                print(f"  {i+1}. {q['text']} (Sheet: {q['sheet']}, Row: {q['row']})")
            if len(questions) > 5:
                print(f"  ... and {len(questions) - 5} more")


if __name__ == "__main__":
    unittest.main()
