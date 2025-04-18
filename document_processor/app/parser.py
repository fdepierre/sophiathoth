import logging
from typing import Dict, List, Any, Tuple
import io
import pandas as pd
import re
from sqlalchemy.orm import Session

from app.models import TenderDocument, TenderSheet, TenderQuestion
from app.storage import minio_client

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parser for Excel files using pandas"""
    
    def __init__(self):
        pass
    
    def parse_excel_file(self, file_content: bytes) -> Dict[str, Any]:
        """
        Parse an Excel file using pandas
        
        Args:
            file_content: The file content as bytes
            
        Returns:
            Dictionary with parsed sheets and metadata
        """
        try:
            # Parse Excel file using pandas
            excel_file = io.BytesIO(file_content)
            dfs = pd.read_excel(excel_file, sheet_name=None)
            
            # Convert pandas DataFrames to dictionaries for JSON serialization
            sheets = {}
            for sheet_name, df in dfs.items():
                # Convert DataFrame to list of dictionaries (rows)
                sheet_data = df.fillna('').to_dict(orient='records')
                sheets[sheet_name] = sheet_data
            
            # Extract potential questions
            questions = self._extract_questions(sheets)
            
            # Get structure
            structure = self._get_structure(sheets, dfs)
            
            return {
                "sheets": sheets,
                "questions": questions,
                "structure": structure
            }
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise
    
    def _extract_questions(self, sheets: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Extract potential questions and their answers from sheets
        
        Args:
            sheets: Dictionary of sheet name to list of row dictionaries
            
        Returns:
            List of potential questions with their answers
        """
        questions = []
        
        # First, try to identify question-answer pairs based on column headers
        for sheet_name, rows in sheets.items():
            # Check if we have columns that might represent questions and answers
            if len(rows) > 0:
                first_row = rows[0]
                question_col = None
                answer_col = None
                
                # Look for question/answer column pairs
                for col_key in first_row.keys():
                    col_name = str(col_key).lower()
                    if 'question' in col_name or 'query' in col_name or 'prompt' in col_name:
                        question_col = col_key
                    elif 'answer' in col_name or 'response' in col_name or 'reply' in col_name:
                        answer_col = col_key
                
                # If we found both question and answer columns, extract pairs
                if question_col and answer_col:
                    logger.info(f"Found question-answer columns in sheet {sheet_name}: {question_col} and {answer_col}")
                    for row_idx, row in enumerate(rows):
                        question_text = row.get(question_col, '')
                        answer_text = row.get(answer_col, '')
                        
                        # Skip empty questions
                        if not question_text or question_text == '':
                            continue
                            
                        if not isinstance(question_text, str):
                            question_text = str(question_text)
                        if not isinstance(answer_text, str):
                            answer_text = str(answer_text)
                        
                        questions.append({
                            "sheet": sheet_name,
                            "row": row_idx,
                            "column": question_col,
                            "answer_column": answer_col,
                            "text": question_text,
                            "context": answer_text
                        })
                    
                    # If we found structured Q&A pairs, continue to next sheet
                    if questions:
                        continue
        
        # Fallback: look for question-like cells and try to find adjacent answers
        for sheet_name, rows in sheets.items():
            for row_idx, row in enumerate(rows):
                for col_key, cell_value in row.items():
                    if not isinstance(cell_value, str):
                        cell_value = str(cell_value)
                    
                    # Simple heuristic: cells ending with ? are likely questions
                    # or containing the word "question"
                    if (cell_value.strip().endswith('?') or 
                        re.search(r'\bquestion\b', cell_value.lower())):
                        
                        # Try to find an answer in adjacent cells
                        answer_text = ""
                        
                        # Check cell to the right (most common for horizontal layouts)
                        if isinstance(col_key, (int, float)):
                            next_col_key = col_key + 1
                            if next_col_key in row:
                                answer_text = row[next_col_key]
                        
                        # Check cell below (for vertical layouts)
                        if not answer_text and row_idx + 1 < len(rows):
                            next_row = rows[row_idx + 1]
                            if col_key in next_row:
                                answer_text = next_row[col_key]
                        
                        if not isinstance(answer_text, str):
                            answer_text = str(answer_text)
                        
                        questions.append({
                            "sheet": sheet_name,
                            "row": row_idx,
                            "column": col_key,
                            "text": cell_value,
                            "context": answer_text if answer_text else "No answer found"
                        })
        
        return questions
    
    def _get_structure(self, sheets: Dict[str, List[Dict[str, Any]]], 
                      dfs: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
        """
        Get the structure of the Excel file
        
        Args:
            sheets: Dictionary of sheet name to list of row dictionaries
            dfs: Dictionary of sheet name to pandas DataFrame
            
        Returns:
            Dictionary with sheet structure information
        """
        structure = {}
        
        for sheet_name, rows in sheets.items():
            df = dfs[sheet_name]
            headers = list(df.columns)
            
            structure[sheet_name] = {
                "row_count": len(rows),
                "headers": headers
            }
        
        return structure
    
    def parse_and_save(
        self, 
        db: Session, 
        file_content: bytes, 
        filename: str, 
        content_type: str,
        user_id: str = None
    ) -> Tuple[TenderDocument, List[TenderSheet], List[TenderQuestion]]:
        """
        Parse an Excel file and save the results to the database
        
        Args:
            db: Database session
            file_content: The file content as bytes
            filename: The original filename
            content_type: The content type of the file
            user_id: Optional user ID
            
        Returns:
            Tuple of (document, sheets, questions)
        """
        # Parse the Excel file
        parsed_data = self.parse_excel_file(file_content)
        
        # Upload to MinIO
        storage_path = minio_client.upload_file(
            file_data=file_content,
            content_type=content_type
        )
        
        # Create document record
        document = TenderDocument(
            filename=storage_path,
            original_filename=filename,
            content_type=content_type,
            size_bytes=len(file_content),
            storage_path=storage_path,
            doc_metadata={"sheet_count": len(parsed_data["sheets"])},
            created_by=user_id
        )
        db.add(document)
        db.flush()  # Get the ID without committing
        
        # Create sheet records
        sheets = []
        for sheet_name, sheet_info in parsed_data["structure"].items():
            sheet = TenderSheet(
                document_id=document.id,
                name=sheet_name,
                row_count=sheet_info["row_count"],
                column_count=len(sheet_info["headers"]),
                headers=sheet_info["headers"]
            )
            db.add(sheet)
            sheets.append(sheet)
        db.flush()
        
        # Create question records
        questions = []
        sheet_map = {sheet.name: sheet.id for sheet in sheets}
        
        for question_data in parsed_data["questions"]:
            sheet_id = sheet_map.get(question_data["sheet"])
            if not sheet_id:
                continue
                
            # Convert column to integer if possible, otherwise use a default value
            column_index = 0  # Default to 0
            try:
                if isinstance(question_data["column"], (int, float)):
                    column_index = int(question_data["column"])
                elif isinstance(question_data["column"], str):
                    if question_data["column"].isdigit():
                        column_index = int(question_data["column"])
                    else:
                        # For non-numeric column headers, we'll use the position in the headers list
                        sheet_info = parsed_data["structure"].get(question_data["sheet"], {})
                        headers = sheet_info.get("headers", [])
                        if headers and question_data["column"] in headers:
                            column_index = headers.index(question_data["column"])
            except (ValueError, TypeError) as e:
                logger.warning(f"Error converting column index: {e}. Using default value 0.")
                column_index = 0  # Fallback to 0 if there's any error
            
            # Get the context/answer from the question data if available
            context = question_data.get("context", "")
            if not context:
                context = f"From sheet: {question_data['sheet']}, row: {question_data['row']}, column: {question_data['column']}"
            
            question = TenderQuestion(
                document_id=document.id,
                sheet_id=sheet_id,
                text=question_data["text"],
                row_index=question_data["row"],
                column_index=column_index,
                context=context
            )
            db.add(question)
            questions.append(question)
        
        db.commit()
        return document, sheets, questions
    
    def parse_excel_direct(self, file_content: bytes) -> Dict[str, pd.DataFrame]:
        """
        Parse Excel file directly to pandas DataFrames
        
        Args:
            file_content: The file content as bytes
            
        Returns:
            Dictionary of sheet name to DataFrame
        """
        try:
            excel_file = io.BytesIO(file_content)
            return pd.read_excel(excel_file, sheet_name=None)
        except Exception as e:
            logger.error(f"Error parsing Excel file with pandas: {e}")
            raise


# Create a singleton instance
excel_parser = ExcelParser()
