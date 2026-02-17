"""
Unit tests for Text Extraction services
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import io

from app.services.text_extraction.extraction_service import (
    TextExtractionService,
    ExtractionResult,
)
from app.services.text_extraction.parsers.pdf_parser import PDFParser
from app.services.text_extraction.parsers.docx_parser import DOCXParser
from app.services.text_extraction.parsers.url_parser import URLParser


class TestTextExtractionService:
    """Test text extraction service"""

    @pytest.fixture
    def extraction_service(self):
        return TextExtractionService()

    @pytest.mark.asyncio
    async def test_extract_from_url(self, extraction_service):
        """Test extracting text from URL"""
        # Arrange
        mock_html = """
        <html>
            <body>
                <article>
                    <h1>Test Title</h1>
                    <p>This is test content.</p>
                </article>
            </body>
        </html>
        """

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_html
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Act
            result = await extraction_service.extract_from_url("https://example.com")

            # Assert
            assert isinstance(result, ExtractionResult)
            assert "Test Title" in result.text
            assert "test content" in result.text
            assert result.source_type == "url"
            assert result.error is None

    @pytest.mark.asyncio
    async def test_extract_from_url_error(self, extraction_service):
        """Test handling URL extraction error"""
        # Arrange
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = Exception("Connection error")

            # Act
            result = await extraction_service.extract_from_url("https://example.com")

            # Assert
            assert result.error is not None
            assert "Connection error" in result.error

    @pytest.mark.asyncio
    async def test_extract_from_file_pdf(self, extraction_service, tmp_path):
        """Test extracting text from PDF file"""
        # Arrange - Create a mock PDF file
        pdf_content = b"%PDF-1.4 fake pdf content"
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(pdf_content)

        with patch.object(PDFParser, "parse", return_value="Extracted PDF text"):
            # Act
            result = await extraction_service.extract_from_file(str(pdf_file))

            # Assert
            assert result.text == "Extracted PDF text"
            assert result.source_type == "pdf"

    @pytest.mark.asyncio
    async def test_extract_from_file_docx(self, extraction_service, tmp_path):
        """Test extracting text from DOCX file"""
        # Arrange
        docx_content = b"fake docx content"
        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(docx_content)

        with patch.object(DOCXParser, "parse", return_value="Extracted DOCX text"):
            # Act
            result = await extraction_service.extract_from_file(str(docx_file))

            # Assert
            assert result.text == "Extracted DOCX text"
            assert result.source_type == "docx"

    @pytest.mark.asyncio
    async def test_extract_from_file_unsupported(self, extraction_service, tmp_path):
        """Test extracting from unsupported file type"""
        # Arrange
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Some text")

        # Act
        result = await extraction_service.extract_from_file(str(txt_file))

        # Assert
        assert result.error is not None
        assert "unsupported" in result.error.lower()

    def test_clean_text(self, extraction_service):
        """Test text cleaning"""
        # Arrange
        raw_text = """
        This   is   a   test.
        
        
        With multiple   spaces   and   lines.
        
        
        End.
        """

        # Act
        cleaned = extraction_service.clean_text(raw_text)

        # Assert
        assert "  " not in cleaned  # No double spaces
        assert cleaned.count("\n\n") <= 1  # No excessive newlines
        assert cleaned.startswith("This is a test")


class TestPDFParser:
    """Test PDF parser"""

    @pytest.fixture
    def pdf_parser(self):
        return PDFParser()

    def test_supported_extensions(self, pdf_parser):
        """Test supported file extensions"""
        assert ".pdf" in pdf_parser.supported_extensions

    @patch("app.services.text_extraction.parsers.pdf_parser.PdfReader")
    def test_parse_success(self, mock_pdf_reader, pdf_parser, tmp_path):
        """Test successful PDF parsing"""
        # Arrange
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page 1 text"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf")

        # Act
        result = pdf_parser.parse(str(pdf_file))

        # Assert
        assert "Page 1 text" in result

    def test_parse_file_not_found(self, pdf_parser):
        """Test parsing non-existent file"""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            pdf_parser.parse("/nonexistent/file.pdf")


class TestDOCXParser:
    """Test DOCX parser"""

    @pytest.fixture
    def docx_parser(self):
        return DOCXParser()

    def test_supported_extensions(self, docx_parser):
        """Test supported file extensions"""
        assert ".docx" in docx_parser.supported_extensions

    @patch("docx.Document")
    def test_parse_success(self, mock_document, docx_parser, tmp_path):
        """Test successful DOCX parsing"""
        # Arrange
        mock_para1 = Mock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = Mock()
        mock_para2.text = "Paragraph 2"

        mock_doc = Mock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_document.return_value = mock_doc

        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"fake docx")

        # Act
        result = docx_parser.parse(str(docx_file))

        # Assert
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result


class TestURLParser:
    """Test URL parser"""

    @pytest.fixture
    def url_parser(self):
        return URLParser()

    def test_supported_schemes(self, url_parser):
        """Test supported URL schemes"""
        assert "http" in url_parser.supported_schemes
        assert "https" in url_parser.supported_schemes

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_parse_success(self, mock_get, url_parser):
        """Test successful URL parsing"""
        # Arrange
        mock_response = Mock()
        mock_response.text = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <nav>Navigation</nav>
                <article>
                    <h1>Article Title</h1>
                    <p>Article content here.</p>
                </article>
                <footer>Footer</footer>
            </body>
        </html>
        """
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Act
        result = await url_parser.parse("https://example.com/article")

        # Assert
        assert "Article Title" in result
        assert "Article content here" in result
        assert "Navigation" not in result  # Should be cleaned
        assert "Footer" not in result  # Should be cleaned

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_parse_http_error(self, mock_get, url_parser):
        """Test handling HTTP error"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception):
            await url_parser.parse("https://example.com/notfound")
