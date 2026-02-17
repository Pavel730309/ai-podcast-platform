"""
ElevenLabs TTS Provider
"""

import os
from typing import List, Optional
import httpx
from app.services.tts.base_provider import (
    BaseTTSProvider,
    Voice,
    TTSResult,
    VoiceGender,
)


class ElevenLabsProvider(BaseTTSProvider):
    """ElevenLabs TTS Provider implementation"""

    provider_name = "elevenlabs"

    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self._voices_cache: Optional[List[Voice]] = None

    async def is_available(self) -> bool:
        """Check if provider is available"""
        return bool(self.api_key)

    async def synthesize(
        self, text: str, voice_id: str, speed: float = 1.0, **kwargs
    ) -> TTSResult:
        """Synthesize text to speech using ElevenLabs"""
        if not self.api_key:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider="elevenlabs",
                voice_id=voice_id,
                error="ElevenLabs API key not configured",
            )

        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key,
            }

            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": kwargs.get("stability", 0.5),
                    "similarity_boost": kwargs.get("similarity_boost", 0.75),
                },
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=data, headers=headers)

                if response.status_code != 200:
                    return TTSResult(
                        audio_data=b"",
                        duration_seconds=0,
                        provider="elevenlabs",
                        voice_id=voice_id,
                        error=f"ElevenLabs API error: {response.text}",
                    )

                audio_data = response.content

                # Estimate duration (rough approximation)
                duration = len(text.split()) * 0.5  # ~0.5s per word

                return TTSResult(
                    audio_data=audio_data,
                    duration_seconds=duration,
                    provider="elevenlabs",
                    voice_id=voice_id,
                    format="mp3",
                )

        except Exception as e:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider="elevenlabs",
                voice_id=voice_id,
                error=f"ElevenLabs synthesis error: {str(e)}",
            )

    async def get_voices(self, language: Optional[str] = None) -> List[Voice]:
        """Get available voices from ElevenLabs"""
        if self._voices_cache:
            return self._filter_voices_by_language(self._voices_cache, language)

        if not self.api_key:
            return self._get_default_voices()

        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    return self._get_default_voices()

                data = response.json()
                voices = []

                for v in data.get("voices", []):
                gender_str = v.get("labels", {}).get("gender", "neutral")
                gender = VoiceGender.NEUTRAL
                if gender_str == "male":
                    gender = VoiceGender.MALE
                elif gender_str == "female":
                    gender = VoiceGender.FEMALE
                
                voice = Voice(
                    id=v["voice_id"],
                    name=v.get("name", "Unknown"),
                    provider="elevenlabs",
                    gender=gender,
                    language="multilingual",
                    description=v.get("description", ""),
                )
                    voices.append(voice)

                self._voices_cache = voices
                return self._filter_voices_by_language(voices, language)

        except Exception:
            return self._get_default_voices()

    def _get_default_voices(self) -> List[Voice]:
        """Get default voices when API is unavailable"""
        return [
            Voice(
                id="21m00Tcm4TlvDq8ikWAM",
                name="Rachel",
                provider="elevenlabs",
                gender=VoiceGender.FEMALE,
                language="multilingual",
                description="Calm and professional female voice",
            ),
            Voice(
                id="AZnzlk1XvdvUeBnXmlld",
                name="Domi",
                provider="elevenlabs",
                gender=VoiceGender.FEMALE,
                language="multilingual",
                description="Strong and energetic female voice",
            ),
            Voice(
                id="EXAVITQu4vr4xnSDxMaL",
                name="Bella",
                provider="elevenlabs",
                gender=VoiceGender.FEMALE,
                language="multilingual",
                description="Soft and gentle female voice",
            ),
            Voice(
                id="ErXwobaYiN019PkySvjV",
                name="Antoni",
                provider="elevenlabs",
                gender=VoiceGender.MALE,
                language="multilingual",
                description="Well-rounded male voice",
            ),
            Voice(
                id="MF3mGyEYCl7XYWbV9V6O",
                name="Elli",
                provider="elevenlabs",
                gender=VoiceGender.FEMALE,
                language="multilingual",
                description="Friendly and casual female voice",
            ),
            Voice(
                id="TxGEqnHWrfWFTfGW9XjX",
                name="Josh",
                provider="elevenlabs",
                gender=VoiceGender.MALE,
                language="multilingual",
                description="Deep male voice",
            ),
        ]

    def _filter_voices_by_language(
        self, voices: List[Voice], language: Optional[str]
    ) -> List[Voice]:
        """Filter voices by language"""
        if not language:
            return voices
        return [
            v for v in voices if v.language == language or v.language == "multilingual"
        ]
