"""
URL Parser for text extraction from web pages
"""
import re
from typing import Optional
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
import trafilatura

from app.services.text_extraction.base_parser import BaseParser, ExtractionResult


class URLParser(BaseParser):
    """Parser for extracting text from URLs"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.supported_schemes = ["http", "https"]
    
    def supports_source(self, source) -> bool:
        """Check if source is a valid URL"""
        if not isinstance(source, str):
            return False
        
        try:
            parsed = urlparse(source)
            return parsed.scheme in self.supported_schemes and bool(parsed.netloc)
        except Exception:
            return False
    
    async def parse(self, source: str) -> ExtractionResult:
        """
        Parse URL and extract text content
        
        Args:
            source: URL to parse
            
        Returns:
            ExtractionResult with extracted text
        """
        if not self.supports_source(source):
            return ExtractionResult(
                text="",
                error=f"Invalid URL: {source}"
            )
        
        try:
            # Try trafilatura first (better for article extraction)
            result = await self._parse_with_trafilatura(source)
            if result.text and not result.error:
                return result
            
            # Fallback to BeautifulSoup
            result = await self._parse_with_beautifulsoup(source)
            return result
            
        except Exception as e:
            return ExtractionResult(
                text="",
                error=f"Error extracting text from URL: {str(e)}"
            )
    
    async def _parse_with_trafilatura(self, url: str) -> ExtractionResult:
        """
        Parse URL using trafilatura library
        
        Args:
            url: URL to parse
            
        Returns:
            ExtractionResult with extracted text
        """
        try:
            # Fetch the webpage
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
            
            html_content = response.text
            
            # Extract text using trafilatura
            extracted = trafilatura.extract(
                html_content,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if not extracted:
                return ExtractionResult(
                    text="",
                    error="Trafilatura could not extract text"
                )
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(html_content)
            
            title = None
            author = None
            
            if metadata:
                title = metadata.get("title")
                author = metadata.get("author")
            
            result = ExtractionResult(
                text=extracted,
                title=title,
                author=author,
                source_type="url"
            )
            
            return self.validate_result(result)
            
        except Exception as e:
            return ExtractionResult(
                text="",
                error=f"Trafilatura extraction failed: {str(e)}"
            )
    
    async def _parse_with_beautifulsoup(self, url: str) -> ExtractionResult:
        """
        Parse URL using BeautifulSoup as fallback
        
        Args:
            url: URL to parse
            
        Returns:
            ExtractionResult with extracted text
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
            
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Try to find main content
            main_content = (
                soup.find("main") or
                soup.find("article") or
                soup.find("div", class_=re.compile(r"content|article|post|entry", re.I)) or
                soup.find("div", id=re.compile(r"content|article|post|entry", re.I)) or
                soup.body
            )
            
            if not main_content:
                main_content = soup
            
            # Extract title
            title = None
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            h1_tag = soup.find("h1")
            if h1_tag:
                title = h1_tag.get_text(strip=True)
            
            # Extract author (common patterns)
            author = None
            author_tag = soup.find("meta", attrs={"name": "author"})
            if author_tag:
                author = author_tag.get("content")
            
            if not author:
                author_tag = soup.find("span", class_=re.compile(r"author", re.I))
                if author_tag:
                    author = author_tag.get_text(strip=True)
            
            # Extract text
            text = main_content.get_text(separator="\n", strip=True)
            
            # Clean up text
            text = self._clean_text(text)
            
            result = ExtractionResult(
                text=text,
                title=title,
                author=author,
                source_type="url"
            )
            
            return self.validate_result(result)
            
        except Exception as e:
            return ExtractionResult(
                text="",
                error=f"BeautifulSoup extraction failed: {str(e)}"
            )
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove common unwanted patterns
        text = re.sub(r'Share this:.*', '', text, flags=re.I)
        text = re.sub(r'Follow us:.*', '', text, flags=re.I)
        text = re.sub(r'Subscribe to our newsletter.*', '', text, flags=re.I)
        
        return text.strip()
