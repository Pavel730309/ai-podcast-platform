"""
Text cleaner for preparing extracted text for AI processing
"""
import re
from typing import List, Optional


class TextCleaner:
    """Clean and format extracted text for AI processing"""
    
    def __init__(self):
        # Patterns for cleaning
        self.multiple_spaces = re.compile(r' +')
        self.multiple_newlines = re.compile(r'\n\s*\n+')
        self.trailing_spaces = re.compile(r'[ \t]+\n')
        self.leading_spaces = re.compile(r'\n[ \t]+')
        
        # Common patterns to remove or fix
        self.url_pattern = re.compile(r'https?://\S+')
        self.email_pattern = re.compile(r'\S+@\S+\.\S+')
        self.phone_pattern = re.compile(r'\+?[\d\s\-\(\)]{7,}')
        
        # Unicode normalization patterns
        self.smart_quotes = {
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...',  # Ellipsis
        }
    
    def clean(self, text: str, 
              remove_urls: bool = False,
              remove_emails: bool = False,
              remove_phones: bool = False) -> str:
        """
        Clean text for AI processing
        
        Args:
            text: Text to clean
            remove_urls: Whether to remove URLs
            remove_emails: Whether to remove email addresses
            remove_phones: Whether to remove phone numbers
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Normalize unicode characters
        text = self._normalize_unicode(text)
        
        # Remove unwanted patterns
        if remove_urls:
            text = self.url_pattern.sub('', text)
        if remove_emails:
            text = self.email_pattern.sub('', text)
        if remove_phones:
            text = self.phone_pattern.sub('', text)
        
        # Fix whitespace
        text = self._fix_whitespace(text)
        
        # Fix punctuation
        text = self._fix_punctuation(text)
        
        # Remove empty lines at start and end
        text = text.strip()
        
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize unicode characters to ASCII equivalents"""
        for unicode_char, ascii_char in self.smart_quotes.items():
            text = text.replace(unicode_char, ascii_char)
        return text
    
    def _fix_whitespace(self, text: str) -> str:
        """Fix whitespace issues"""
        # Remove trailing spaces on lines
        text = self.trailing_spaces.sub('\n', text)
        
        # Remove leading spaces on lines (preserve indentation structure)
        text = self.leading_spaces.sub('\n', text)
        
        # Replace multiple spaces with single space
        text = self.multiple_spaces.sub(' ', text)
        
        # Replace multiple newlines with double newline
        text = self.multiple_newlines.sub('\n\n', text)
        
        return text
    
    def _fix_punctuation(self, text: str) -> str:
        """Fix common punctuation issues"""
        # Fix space before punctuation
        text = re.sub(r' +([.,!?;:])', r'\1', text)
        
        # Fix missing space after punctuation
        text = re.sub(r'([.,!?;:])([A-Za-zА-Яа-я])', r'\1 \2', text)
        
        # Fix multiple punctuation
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with NLP libraries)
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs
        
        Args:
            text: Text to split
            
        Returns:
            List of paragraphs
        """
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def extract_key_phrases(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract key phrases from text (simple approach)
        
        Args:
            text: Text to extract phrases from
            min_length: Minimum word count for a phrase
            
        Returns:
            List of key phrases
        """
        # This is a simple implementation
        # For better results, use NLP libraries like spaCy
        sentences = self.split_into_sentences(text)
        phrases = []
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) >= min_length:
                phrases.append(sentence)
        
        return phrases
    
    def estimate_reading_time(self, text: str, words_per_minute: int = 150) -> int:
        """
        Estimate reading time in minutes
        
        Args:
            text: Text to estimate
            words_per_minute: Reading speed
            
        Returns:
            Estimated reading time in minutes
        """
        word_count = len(text.split())
        minutes = word_count / words_per_minute
        return max(1, round(minutes))
    
    def get_text_stats(self, text: str) -> dict:
        """
        Get text statistics
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with text statistics
        """
        words = text.split()
        sentences = self.split_into_sentences(text)
        paragraphs = self.split_into_paragraphs(text)
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "average_sentence_length": len(words) / len(sentences) if sentences else 0,
            "estimated_reading_time_minutes": self.estimate_reading_time(text)
        }
    
    def truncate_text(self, text: str, max_words: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum word count
        
        Args:
            text: Text to truncate
            max_words: Maximum number of words
            suffix: Suffix to add when truncated
            
        Returns:
            Truncated text
        """
        words = text.split()
        if len(words) <= max_words:
            return text
        
        truncated = ' '.join(words[:max_words])
        return f"{truncated}{suffix}"
    
    def prepare_for_tts(self, text: str) -> str:
        """
        Prepare text specifically for TTS processing
        
        Args:
            text: Text to prepare
            
        Returns:
            Text optimized for TTS
        """
        # Clean the text
        text = self.clean(text)
        
        # Remove URLs, emails, and phones for TTS
        text = self.url_pattern.sub('', text)
        text = self.email_pattern.sub('', text)
        
        # Replace abbreviations with full words (basic set)
        abbreviations = {
            'Mr.': 'Mister',
            'Mrs.': 'Misses',
            'Ms.': 'Miss',
            'Dr.': 'Doctor',
            'Prof.': 'Professor',
            'vs.': 'versus',
            'etc.': 'etcetera',
            'e.g.': 'for example',
            'i.e.': 'that is',
            'approx.': 'approximately',
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        # Clean up any resulting issues
        text = self._fix_whitespace(text)
        
        return text
