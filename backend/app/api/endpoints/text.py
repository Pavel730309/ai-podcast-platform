"""
API endpoints for text extraction
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import os
import uuid
from pathlib import Path

from app.schemas import (
    TextExtractionRequest,
    TextExtractionResponse,
    FileUploadResponse
)
from app.services.text_extraction import TextExtractionService
from app.config import settings

router = APIRouter(prefix="/text", tags=["text-extraction"])

# Initialize service
extraction_service = TextExtractionService()


@router.post("/extract", response_model=TextExtractionResponse)
async def extract_text(request: TextExtractionRequest):
    """
    Extract text from URL or raw text
    
    - **source_type**: Type of source (url, text)
    - **url**: URL to extract text from (required if source_type is url)
    - **text**: Raw text to process (required if source_type is text)
    """
    if request.source_type == "url":
        if not request.url:
            raise HTTPException(status_code=400, detail="URL is required for URL source type")
        
        result = await extraction_service.extract_from_url(request.url)
        
        if result.error:
            raise HTTPException(status_code=400, detail=result.error)
        
        stats = extraction_service.get_text_stats(result.text)
        
        return TextExtractionResponse(
            text=result.text,
            title=result.title,
            author=result.author,
            source_type=result.source_type,
            word_count=stats["word_count"],
            character_count=stats["character_count"],
            estimated_reading_time=stats["estimated_reading_time_minutes"]
        )
    
    elif request.source_type == "text":
        if not request.text:
            raise HTTPException(status_code=400, detail="Text is required for text source type")
        
        # Clean the text
        cleaned_text = extraction_service.cleaner.clean(request.text)
        stats = extraction_service.get_text_stats(cleaned_text)
        
        return TextExtractionResponse(
            text=cleaned_text,
            title=None,
            author=None,
            source_type="text",
            word_count=stats["word_count"],
            character_count=stats["character_count"],
            estimated_reading_time=stats["estimated_reading_time_minutes"]
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {request.source_type}")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for text extraction
    
    - **file**: File to upload (PDF or DOCX)
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)} MB"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file with unique name
    file_path = upload_dir / f"{file_id}{file_ext}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_type=file_ext[1:],  # Remove the dot
        file_size=len(content)
    )


@router.post("/extract/{file_id}", response_model=TextExtractionResponse)
async def extract_from_uploaded_file(file_id: str):
    """
    Extract text from an uploaded file
    
    - **file_id**: ID of the uploaded file
    """
    # Find the file
    upload_dir = Path(settings.UPLOAD_DIR)
    
    # Look for file with any allowed extension
    file_path = None
    for ext in settings.ALLOWED_EXTENSIONS:
        potential_path = upload_dir / f"{file_id}{ext}"
        if potential_path.exists():
            file_path = potential_path
            break
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Extract text
    result = await extraction_service.extract_from_file(str(file_path))
    
    if result.error:
        raise HTTPException(status_code=400, detail=result.error)
    
    stats = extraction_service.get_text_stats(result.text)
    
    return TextExtractionResponse(
        text=result.text,
        title=result.title,
        author=result.author,
        source_type=result.source_type,
        word_count=stats["word_count"],
        character_count=stats["character_count"],
        estimated_reading_time=stats["estimated_reading_time_minutes"]
    )


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "formats": extraction_service.get_supported_formats(),
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
    }
