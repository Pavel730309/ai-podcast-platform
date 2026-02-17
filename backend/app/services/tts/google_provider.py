"""
Google Cloud TTS Provider
"""

import os
from typing import List, Optional
from google.cloud import texttospeech
from google.oauth2 import service_account
from app.services.tts.base_provider import BaseTTSProvider, Voice, TTSResult


class GoogleTTSProvider(BaseTTSProvider):
    """Google Cloud Text-to-Speech Provider implementation"""

    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self._client: Optional[texttospeech.TextToSpeechClient] = None
        self._voices_cache: Optional[List[Voice]] = None

    def _get_client(self) -> Optional[texttospeech.TextToSpeechClient]:
        """Get or create TTS client"""
        if self._client:
            return self._client

        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self._client = texttospeech.TextToSpeechClient(credentials=credentials)
            else:
                # Try to use default credentials
                self._client = texttospeech.TextToSpeechClient()
            return self._client
        except Exception:
            return None

    async def is_available(self) -> bool:
        """Check if provider is available"""
        try:
            client = self._get_client()
            return client is not None
        except Exception:
            return False

    async def synthesize(
        self, text: str, voice_id: str, speed: float = 1.0, **kwargs
    ) -> TTSResult:
        """Synthesize text to speech using Google Cloud"""
        try:
            client = self._get_client()
            if not client:
                return TTSResult(
                    audio_data=b"",
                    duration_seconds=0,
                    provider="google",
                    voice_id=voice_id,
                    error="Google Cloud TTS client not available",
                )

            # Parse voice_id (format: "languageCode-voiceName")
            parts = voice_id.split("-")
            if len(parts) >= 2:
                language_code = parts[0]
                voice_name = voice_id
            else:
                language_code = "en-US"
                voice_name = voice_id

            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
            )

            # Select the audio format
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed,
                pitch=kwargs.get("pitch", 0.0),
            )

            # Build the synthesis request
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Perform the request
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )

            # Estimate duration
            duration = len(text.split()) * 0.5

            return TTSResult(
                audio_data=response.audio_content,
                duration_seconds=duration,
                provider="google",
                voice_id=voice_id,
                format="mp3",
            )

        except Exception as e:
            return TTSResult(
                audio_data=b"",
                duration_seconds=0,
                provider="google",
                voice_id=voice_id,
                error=f"Google TTS error: {str(e)}",
            )

    async def get_voices(self, language: Optional[str] = None) -> List[Voice]:
        """Get available voices from Google Cloud"""
        if self._voices_cache:
            return self._filter_voices(self._voices_cache, language)

        try:
            client = self._get_client()
            if not client:
                return self._get_default_voices()

            # Fetch voices from API
            voices_response = client.list_voices()
            voices = []

            for v in voices_response.voices:
                # Only include WaveNet and Neural2 voices for quality
                voice_name = v.name
                if "WaveNet" not in voice_name and "Neural2" not in voice_name:
                    continue

                # Determine gender
                gender_map = {
                    texttospeech.SsmlVoiceGender.MALE: "male",
                    texttospeech.SsmlVoiceGender.FEMALE: "female",
                    texttospeech.SsmlVoiceGender.NEUTRAL: "neutral",
                }
                gender = gender_map.get(v.ssml_gender, "neutral")

                voice = Voice(
                    id=voice_name,
                    name=voice_name.split("-")[-1],
                    provider="google",
                    gender=gender,
                    language=v.language_codes[0] if v.language_codes else "en-US",
                    description=f"{voice_name} - {gender}",
                )
                voices.append(voice)

            self._voices_cache = voices
            return self._filter_voices(voices, language)

        except Exception:
            return self._get_default_voices()

    def _get_default_voices(self) -> List[Voice]:
        """Get default voices when API is unavailable"""
        return [
            Voice(
                id="en-US-Neural2-A",
                name="Neural2-A",
                provider="google",
                gender="male",
                language="en-US",
                description="Neural2 male voice",
            ),
            Voice(
                id="en-US-Neural2-C",
                name="Neural2-C",
                provider="google",
                gender="female",
                language="en-US",
                description="Neural2 female voice",
            ),
            Voice(
                id="en-US-Neural2-D",
                name="Neural2-D",
                provider="google",
                gender="male",
                language="en-US",
                description="Neural2 male voice",
            ),
            Voice(
                id="en-US-Neural2-E",
                name="Neural2-E",
                provider="google",
                gender="female",
                language="en-US",
                description="Neural2 female voice",
            ),
            Voice(
                id="en-US-Neural2-F",
                name="Neural2-F",
                provider="google",
                gender="female",
                language="en-US",
                description="Neural2 female voice",
            ),
            Voice(
                id="en-US-Wavenet-A",
                name="Wavenet-A",
                provider="google",
                gender="male",
                language="en-US",
                description="WaveNet male voice",
            ),
        ]

    def _filter_voices(
        self, voices: List[Voice], language: Optional[str]
    ) -> List[Voice]:
        """Filter voices by language and quality"""
        filtered = voices

        if language:
            filtered = [v for v in filtered if v.language.startswith(language)]

        # Sort by quality (Neural2 > WaveNet > Standard)
        def quality_score(voice: Voice) -> int:
            if "Neural2" in voice.id:
                return 2
            elif "WaveNet" in voice.id:
                return 1
            return 0

        return sorted(filtered, key=quality_score, reverse=True)
