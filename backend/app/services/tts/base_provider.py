"""
Base TTS provider interface
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


@dataclass
class Voice:
    """Voice profile"""
    id: str
    name: str
    provider: str
    gender: VoiceGender
    language: str = "en"
    description: Optional[str] = None
    preview_url: Optional[str] = None


@dataclass
class TTSResult:
    """Result of TTS synthesis"""
    audio_data: bytes
    duration_seconds: float
    provider: str
    voice_id: str
    format: str = "mp3"
    error: Optional[str] = None
    file_path: Optional[str] = None  # Path to saved audio file (for large files)


class BaseTTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        **kwargs
    ) -> TTSResult:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice_id: Voice identifier
            speed: Speech speed (0.5 to 2.0)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            TTSResult with audio data
        """
        pass
    
    @abstractmethod
    async def get_voices(self, language: Optional[str] = None) -> List[Voice]:
        """
        Get available voices
        
        Args:
            language: Filter by language code (optional)
            
        Returns:
            List of available voices
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the TTS provider is available"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name"""
        pass
