from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models import TenderDocument, TenderSheet, TenderQuestion
from app.schemas import (
    TenderDocumentResponse, 
    TenderSheetResponse, 
    TenderQuestionResponse,
    ParsedExcelResponse
)
from app.parser import excel_parser

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ParsedExcelResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = None  # Would come from auth middleware
):
    """
    Upload and parse an Excel tender document
    """
    # Validate file type
    if not file.content_type in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream"
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only Excel files are supported."
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse and save the document
        document, sheets, questions = excel_parser.parse_and_save(
            db=db,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
            user_id=user_id
        )
        
        return ParsedExcelResponse(
            document_id=document.id,
            sheet_count=len(sheets),
            question_count=len(questions),
            metadata=document.metadata or {}
        )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/", response_model=List[TenderDocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all tender documents
    """
    documents = db.query(TenderDocument).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=TenderDocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tender document
    """
    document = db.query(TenderDocument).filter(TenderDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.get("/{document_id}/sheets", response_model=List[TenderSheetResponse])
def get_document_sheets(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all sheets for a specific tender document
    """
    document = db.query(TenderDocument).filter(TenderDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document.sheets


@router.get("/{document_id}/questions", response_model=List[TenderQuestionResponse])
def get_document_questions(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all questions for a specific tender document
    """
    document = db.query(TenderDocument).filter(TenderDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document.questions


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a specific tender document
    """
    document = db.query(TenderDocument).filter(TenderDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete the file from storage
    from app.storage import minio_client
    minio_client.delete_file(document.storage_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return None
