"""
OpenAI TTS provider
"""
from typing import Optional, List
import openai

from app.services.tts.base_provider import (
    BaseTTSProvider,
    Voice,
    VoiceGender,
    TTSResult
)
from app.config import settings


class OpenAITTSProvider(BaseTTSProvider):
    """OpenAI TTS provider implementation"""
    
    # Available OpenAI voices
    AVAILABLE_VOICES = [
        Voice(
            id="alloy",
            name="Alloy",
            provider="openai",
            gender=VoiceGender.NEUTRAL,
            language="en",
            description="A neutral, balanced voice"
        ),
        Voice(
            id="echo",
            name="Echo",
            provider="openai",
            gender=VoiceGender.MALE,
            language="en",
            description="A warm, conversational male voice"
        ),
        Voice(
            id="fable",
            name="Fable",
            provider="openai",
            gender=VoiceGender.NEUTRAL,
            language="en",
            description="A expressive, storytelling voice"
        ),
        Voice(
            id="onyx",
            name="Onyx",
            provider="openai",
            gender=VoiceGender.MALE,
            language="en",
            description="A deep, authoritative male voice"
        ),
        Voice(
            id="nova",
            name="Nova",
            provider="openai",
            gender=VoiceGender.FEMALE,
            language="en",
            description="A friendly, clear female voice"
        ),
        Voice(
            id="shimmer",
            name="Shimmer",
            provider="openai",
            gender=VoiceGender.FEMALE,
            language="en",
            description="A soft, warm female voice"
        )
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.client is not None
    
    async def synthesize(
        self,
        text: str,
        voice_id: str = "alloy",
        speed: float = 1.0,
        model: str = "tts-1",
        **kwargs
    ) -> TTSResult:
        """
        Synthesize speech using OpenAI TTS API
        
        Args:
            text: Text to synthesize (max 4096 characters)
            voice_id: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)
            model: Model to use (tts-1 or tts-1-hd)
            
        Returns:
            TTSResult with audio data
        """
        if not self.client:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider=self.provider_name,
                voice_id=voice_id,
                error="OpenAI API key not configured"
            )
        
        # Validate inputs
        if not text:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider=self.provider_name,
                voice_id=voice_id,
                error="Text cannot be empty"
            )
        
        if len(text) > 4096:
            # Truncate text to max length
            text = text[:4096]
        
        # Clamp speed
        speed = max(0.25, min(4.0, speed))
        
        # Validate voice
        if voice_id not in [v.id for v in self.AVAILABLE_VOICES]:
            voice_id = "alloy"
        
        try:
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice_id,
                input=text,
                speed=speed,
                response_format="mp3"
            )
            
            # Get audio data
            audio_data = response.content
            
            # Estimate duration (rough estimate based on text length and speed)
            # Average speaking rate: ~150 words per minute
            words = len(text.split())
            duration_seconds = (words / 150) * 60 / speed
            
            return TTSResult(
                audio_data=audio_data,
                duration_seconds=duration_seconds,
                provider=self.provider_name,
                voice_id=voice_id,
                format="mp3"
            )
            
        except openai.APIError as e:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider=self.provider_name,
                voice_id=voice_id,
                error=f"OpenAI API error: {str(e)}"
            )
        except Exception as e:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider=self.provider_name,
                voice_id=voice_id,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def get_voices(self, language: Optional[str] = None) -> List[Voice]:
        """
        Get available OpenAI voices
        
        Args:
            language: Filter by language (OpenAI only supports English)
            
        Returns:
            List of available voices
        """
        if language and language.lower() != "en":
            return []
        
        return self.AVAILABLE_VOICES
