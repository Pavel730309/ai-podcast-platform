"""
DOCX Parser for text extraction
"""
import io
from typing import Union
from docx import Document

from app.services.text_extraction.base_parser import BaseParser, ExtractionResult


class DOCXParser(BaseParser):
    """Parser for DOCX documents"""
    
    def __init__(self):
        self.supported_extensions = [".docx"]
    
    def supports_source(self, source) -> bool:
        """Check if source is a DOCX file"""
        if isinstance(source, str):
            return source.lower().endswith(".docx")
        elif isinstance(source, bytes):
            # DOCX files are ZIP archives with specific structure
            # Check for ZIP magic bytes and DOCX-specific content
            return source[:4] == b'PK\x03\x04'
        return False
    
    async def parse(self, source: Union[str, bytes]) -> ExtractionResult:
        """
        Parse DOCX and extract text
        
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
                error=f"Error parsing DOCX: {str(e)}"
            )
    
    async def _parse_file(self, file_path: str) -> ExtractionResult:
        """Parse DOCX from file path"""
        try:
            doc = Document(file_path)
            return self._extract_from_document(doc)
        except Exception as e:
            return ExtractionResult(
                text="",
                error=f"Error parsing DOCX file: {str(e)}"
            )
    
    async def _parse_bytes(self, content: bytes) -> ExtractionResult:
        """Parse DOCX from bytes"""
        try:
            doc = Document(io.BytesIO(content))
            return self._extract_from_document(doc)
        except Exception as e:
            return ExtractionResult(
                text="",
                error=f"Error parsing DOCX content: {str(e)}"
            )
    
    def _extract_from_document(self, doc: Document) -> ExtractionResult:
        """
        Extract text from python-docx Document object
        
        Args:
            doc: Document object from python-docx
            
        Returns:
            ExtractionResult with extracted text
        """
        text_parts = []
        metadata = {}
        
        # Extract core properties/metadata
        try:
            core_props = doc.core_properties
            if core_props.title:
                metadata["title"] = core_props.title
            if core_props.author:
                metadata["author"] = core_props.author
        except Exception:
            pass  # Metadata extraction is optional
        
        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            para_text = paragraph.text.strip()
            if para_text:
                # Check if it's a heading
                if paragraph.style.name.startswith('Heading'):
                    text_parts.append(f"\n## {para_text}\n")
                else:
                    text_parts.append(para_text)
        
        # Extract text from tables
        for table in doc.tables:
            table_text = self._extract_table_text(table)
            if table_text:
                text_parts.append(f"\n{table_text}\n")
        
        full_text = "\n".join(text_parts)
        
        result = ExtractionResult(
            text=full_text,
            title=metadata.get("title"),
            author=metadata.get("author"),
            source_type="docx"
        )
        
        return self.validate_result(result)
    
    def _extract_table_text(self, table) -> str:
        """
        Extract text from a table
        
        Args:
            table: Table object from python-docx
            
        Returns:
            Formatted table text
        """
        rows_text = []
        for row in table.rows:
            cells_text = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    cells_text.append(cell_text)
            if cells_text:
                rows_text.append(" | ".join(cells_text))
        
        return "\n".join(rows_text)
