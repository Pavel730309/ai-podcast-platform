"""
Base parser interface for text extraction
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractionResult:
    """Result of text extraction"""
    text: str
    title: Optional[str] = None
    author: Optional[str] = None
    source_type: str = "unknown"
    word_count: int = 0
    error: Optional[str] = None
    
    def __post_init__(self):
        """Calculate word count after initialization"""
        if self.text and self.word_count == 0:
            self.word_count = len(self.text.split())


class BaseParser(ABC):
    """Abstract base class for text parsers"""
    
    @abstractmethod
    async def parse(self, source) -> ExtractionResult:
        """
        Parse source and extract text
        
        Args:
            source: Source to parse (file path, bytes, URL, etc.)
            
        Returns:
            ExtractionResult with extracted text and metadata
        """
        pass
    
    @abstractmethod
    def supports_source(self, source) -> bool:
        """
        Check if parser supports the given source
        
        Args:
            source: Source to check
            
        Returns:
            True if parser can handle this source
        """
        pass
    
    def validate_result(self, result: ExtractionResult) -> ExtractionResult:
        """
        Validate extraction result
        
        Args:
            result: Extraction result to validate
            
        Returns:
            Validated result with error message if validation failed
        """
        if not result.text or len(result.text.strip()) == 0:
            result.error = "No text could be extracted from the source"
        return result
