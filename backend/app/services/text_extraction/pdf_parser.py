"""
PDF Parser for text extraction
"""
import io
from typing import Union, Optional
import pdfplumber
from PyPDF2 import PdfReader

from app.services.text_extraction.base_parser import BaseParser, ExtractionResult


class PDFParser(BaseParser):
    """Parser for PDF documents"""
    
    def __init__(self):
        self.supported_extensions = [".pdf"]
    
    def supports_source(self, source) -> bool:
        """Check if source is a PDF file"""
        if isinstance(source, str):
            return source.lower().endswith(".pdf")
        elif isinstance(source, bytes):
            # Try to detect PDF by magic bytes
            return source[:4] == b'%PDF'
        return False
    
    async def parse(self, source: Union[str, bytes]) -> ExtractionResult:
        """
        Parse PDF and extract text
        
        Args:
            source: File path (str) or file content (bytes)
            
        Returns:
            ExtractionResult with extracted text
        """
        try:
            if isinstance(source, bytes):
                return await self._parse_bytes(source)
            elif isinstance(source, str):
                return await self._parse_file(source)
            else:
                return ExtractionResult(
                    text="",
                    error=f"Unsupported source type: {type(source)}"
                )
        except Exception as e:
            return ExtractionResult(
                text="",
                error=f"Error parsing PDF: {str(e)}"
            )
    
    async def _parse_file(self, file_path: str) -> ExtractionResult:
        """Parse PDF from file path"""
        text_parts = []
        metadata = {}
        
        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                if pdf.metadata:
                    metadata["title"] = pdf.metadata.get("Title")
                    metadata["author"] = pdf.metadata.get("Author")
                
                # Extract text from each page
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            full_text = "\n\n".join(text_parts)
            
            result = ExtractionResult(
                text=full_text,
                title=metadata.get("title"),
                author=metadata.get("author"),
                source_type="pdf"
            )
            
            return self.validate_result(result)
            
        except Exception as e:
            # Fallback to PyPDF2
            try:
                return await self._parse_with_pypdf2_file(file_path)
            except Exception as e2:
                return ExtractionResult(
                    text="",
                    error=f"Error parsing PDF: {str(e2)}"
                )
    
    async def _parse_bytes(self, content: bytes) -> ExtractionResult:
        """Parse PDF from bytes"""
        text_parts = []
        metadata = {}
        
        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                # Extract metadata
                if pdf.metadata:
                    metadata["title"] = pdf.metadata.get("Title")
                    metadata["author"] = pdf.metadata.get("Author")
                
                # Extract text from each page
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            full_text = "\n\n".join(text_parts)
            
            result = ExtractionResult(
                text=full_text,
                title=metadata.get("title"),
                author=metadata.get("author"),
                source_type="pdf"
            )
            
            return self.validate_result(result)
            
        except Exception as e:
            # Fallback to PyPDF2
            try:
                return await self._parse_with_pypdf2_bytes(content)
            except Exception as e2:
                return ExtractionResult(
                    text="",
                    error=f"Error parsing PDF: {str(e2)}"
                )
    
    async def _parse_with_pypdf2_file(self, file_path: str) -> ExtractionResult:
        """Fallback parsing with PyPDF2 from file"""
        text_parts = []
        metadata = {}
        
        reader = PdfReader(file_path)
        
        # Extract metadata
        if reader.metadata:
            metadata["title"] = reader.metadata.get("/Title")
            metadata["author"] = reader.metadata.get("/Author")
        
        # Extract text from each page
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        full_text = "\n\n".join(text_parts)
        
        result = ExtractionResult(
            text=full_text,
            title=metadata.get("title"),
            author=metadata.get("author"),
            source_type="pdf"
        )
        
        return self.validate_result(result)
    
    async def _parse_with_pypdf2_bytes(self, content: bytes) -> ExtractionResult:
        """Fallback parsing with PyPDF2 from bytes"""
        text_parts = []
        metadata = {}
        
        reader = PdfReader(io.BytesIO(content))
        
        # Extract metadata
        if reader.metadata:
            metadata["title"] = reader.metadata.get("/Title")
            metadata["author"] = reader.metadata.get("/Author")
        
        # Extract text from each page
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        full_text = "\n\n".join(text_parts)
        
        result = ExtractionResult(
            text=full_text,
            title=metadata.get("title"),
            author=metadata.get("author"),
            source_type="pdf"
        )
        
        return self.validate_result(result)
