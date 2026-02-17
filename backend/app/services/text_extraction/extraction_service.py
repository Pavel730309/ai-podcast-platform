"""
Text extraction service that combines all parsers
"""
from typing import Union, Optional
import os
from pathlib import Path

from app.services.text_extraction.base_parser import BaseParser, ExtractionResult
from app.services.text_extraction.pdf_parser import PDFParser
from app.services.text_extraction.docx_parser import DOCXParser
from app.services.text_extraction.url_parser import URLParser
from app.services.text_extraction.text_cleaner import TextCleaner


class TextExtractionService:
    """
    Service for extracting text from various sources
    """
    
    def __init__(self):
        self.parsers: list[BaseParser] = [
            PDFParser(),
            DOCXParser(),
            URLParser()
        ]
        self.cleaner = TextCleaner()
    
    def register_parser(self, parser: BaseParser):
        """Register a new parser"""
        self.parsers.append(parser)
    
    async def extract_from_file(self, file_path: str, clean: bool = True) -> ExtractionResult:
        """
        Extract text from a file
        
        Args:
            file_path: Path to the file
            clean: Whether to clean the extracted text
            
        Returns:
            ExtractionResult with extracted text
        """
        if not os.path.exists(file_path):
            return ExtractionResult(
                text="",
                error=f"File not found: {file_path}"
            )
        
        # Find appropriate parser
        parser = self._get_parser_for_file(file_path)
        if not parser:
            return ExtractionResult(
                text="",
                error=f"No parser found for file: {file_path}"
            )
        
        # Parse the file
        result = await parser.parse(file_path)
        
        # Clean if requested and extraction was successful
        if clean and result.text and not result.error:
            result.text = self.cleaner.clean(result.text)
        
        return result
    
    async def extract_from_bytes(self, 
                                  content: bytes, 
                                  filename: Optional[str] = None,
                                  clean: bool = True) -> ExtractionResult:
        """
        Extract text from file content (bytes)
        
        Args:
            content: File content as bytes
            filename: Optional filename to help determine format
            clean: Whether to clean the extracted text
            
        Returns:
            ExtractionResult with extracted text
        """
        # Try to find parser by filename extension
        parser = None
        if filename:
            parser = self._get_parser_for_file(filename)
        
        # If no parser found by filename, try all parsers
        if not parser:
            parser = self._get_parser_for_bytes(content)
        
        if not parser:
            return ExtractionResult(
                text="",
                error="Could not determine file format"
            )
        
        # Parse the content
        result = await parser.parse(content)
        
        # Clean if requested and extraction was successful
        if clean and result.text and not result.error:
            result.text = self.cleaner.clean(result.text)
        
        return result
    
    async def extract_from_url(self, url: str, clean: bool = True) -> ExtractionResult:
        """
        Extract text from a URL
        
        Args:
            url: URL to extract text from
            clean: Whether to clean the extracted text
            
        Returns:
            ExtractionResult with extracted text
        """
        # Find URL parser
        parser = self._get_url_parser()
        if not parser:
            return ExtractionResult(
                text="",
                error="URL parser not available"
            )
        
        # Parse the URL
        result = await parser.parse(url)
        
        # Clean if requested and extraction was successful
        if clean and result.text and not result.error:
            result.text = self.cleaner.clean(result.text)
        
        return result
    
    async def extract(self, 
                      source: Union[str, bytes],
                      source_type: Optional[str] = None,
                      clean: bool = True) -> ExtractionResult:
        """
        Extract text from any supported source
        
        Args:
            source: Source to extract from (file path, URL, or bytes)
            source_type: Optional hint about source type ('file', 'url', 'bytes')
            clean: Whether to clean the extracted text
            
        Returns:
            ExtractionResult with extracted text
        """
        # Determine source type and extract accordingly
        if source_type == "url" or (isinstance(source, str) and self._is_url(source)):
            return await self.extract_from_url(source, clean)
        
        elif source_type == "file" or (isinstance(source, str) and os.path.exists(source)):
            return await self.extract_from_file(source, clean)
        
        elif isinstance(source, bytes):
            return await self.extract_from_bytes(source, clean=clean)
        
        elif isinstance(source, str):
            # Could be a file path that doesn't exist, or raw text
            # Try to parse as URL first
            if self._is_url(source):
                return await self.extract_from_url(source, clean)
            
            # Otherwise, treat as raw text
            result = ExtractionResult(
                text=source,
                source_type="text"
            )
            if clean:
                result.text = self.cleaner.clean(result.text)
            return result
        
        else:
            return ExtractionResult(
                text="",
                error=f"Unsupported source type: {type(source)}"
            )
    
    def _get_parser_for_file(self, file_path: str) -> Optional[BaseParser]:
        """Get appropriate parser for a file"""
        for parser in self.parsers:
            if parser.supports_source(file_path):
                return parser
        return None
    
    def _get_parser_for_bytes(self, content: bytes) -> Optional[BaseParser]:
        """Get appropriate parser for bytes content"""
        for parser in self.parsers:
            if parser.supports_source(content):
                return parser
        return None
    
    def _get_url_parser(self) -> Optional[BaseParser]:
        """Get URL parser"""
        for parser in self.parsers:
            if isinstance(parser, URLParser):
                return parser
        return None
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL"""
        url_parser = self._get_url_parser()
        if url_parser:
            return url_parser.supports_source(source)
        return False
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported file formats"""
        formats = []
        for parser in self.parsers:
            if hasattr(parser, 'supported_extensions'):
                formats.extend(parser.supported_extensions)
            if hasattr(parser, 'supported_schemes'):
                formats.extend(parser.supported_schemes)
        return list(set(formats))
    
    def get_text_stats(self, text: str) -> dict:
        """Get statistics about the text"""
        return self.cleaner.get_text_stats(text)
    
    def prepare_for_tts(self, text: str) -> str:
        """Prepare text for TTS processing"""
        return self.cleaner.prepare_for_tts(text)
