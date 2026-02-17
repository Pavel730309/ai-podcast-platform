"""
KIE.ai TTS provider
"""
from typing import List, Optional
import httpx
from app.services.tts.base_provider import (
    BaseTTSProvider,
    Voice,
    VoiceGender,
    TTSResult
)
from app.config import settings


class KIEProvider(BaseTTSProvider):
    """KIE.ai TTS provider implementation"""
    
    provider_name = "kie"
    
    # Available voices from KIE.ai
    AVAILABLE_VOICES = [
        Voice(
            id="female-1",
            name="Female Voice 1",
            provider="kie",
            gender=VoiceGender.FEMALE,
            language="ru",
            description="Professional female voice"
        ),
        Voice(
            id="female-2",
            name="Female Voice 2",
            provider="kie",
            gender=VoiceGender.FEMALE,
            language="ru",
            description="Friendly female voice"
        ),
        Voice(
            id="male-1",
            name="Male Voice 1",
            provider="kie",
            gender=VoiceGender.MALE,
            language="ru",
            description="Professional male voice"
        ),
        Voice(
            id="male-2",
            name="Male Voice 2",
            provider="kie",
            gender=VoiceGender.MALE,
            language="ru",
            description="Conversational male voice"
        ),
        Voice(
            id="neutral",
            name="Neutral Voice",
            provider="kie",
            gender=VoiceGender.NEUTRAL,
            language="ru",
            description="Neutral, balanced voice"
        )
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.KIE_API_KEY
        self.base_url = "https://kie.ai/api"
        self._voices_cache: Optional[List[Voice]] = None
    
    @property
    def provider_name(self) -> str:
        return self.provider_name
    
    async def is_available(self) -> bool:
        """Check if KIE.ai API is available"""
        return bool(self.api_key)
    
    async def synthesize(
        self,
        text: str,
        voice_id: str = "neutral",
        speed: float = 1.0,
        **kwargs
    ) -> TTSResult:
        """
        Synthesize speech using KIE.ai TTS API
        
        Args:
            text: Text to synthesize (max 4096 characters)
            voice_id: Voice ID (female-1, female-2, male-1, male-2, neutral)
            speed: Speech speed (0.25 to 4.0)
            
        Returns:
            TTSResult with audio data
        """
        if not self.api_key:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider=self.provider_name,
                voice_id=voice_id,
                error="KIE.ai API key not configured"
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
            voice_id = "neutral"
        
        try:
            # Call KIE.ai TTS API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/audio/speech",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "tts",
                        "voice": voice_id,
                        "input": text,
                        "speed": speed,
                        "response_format": "mp3"
                    }
                )
                
                if response.status_code != 200:
                    return TTSResult(
                        audio_data=b"",
                        duration_seconds=0,
                        provider=self.provider_name,
                        voice_id=voice_id,
                        error=f"KIE.ai API error: {response.text}"
                    )
                
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
                
        except Exception as e:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider=self.provider_name,
                voice_id=voice_id,
                error=f"KIE.ai synthesis error: {str(e)}"
            )
    
    async def get_voices(self, language: Optional[str] = None) -> List[Voice]:
        """
        Get available KIE.ai voices
        
        Args:
            language: Filter by language (KIE.ai supports Russian)
            
        Returns:
            List of available voices
        """
        if language and language.lower() != "ru":
            return []
        
        return self.AVAILABLE_VOICES
